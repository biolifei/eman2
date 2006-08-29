#include "emdata.h"
#include "util.h"
#include "emutil.h"

#include "pca.h"
#include "lapackblas.h"

using namespace EMAN;

// return all right singular vectors
vector <EMData*> PCA::dopca(vector <EMData*> imgstack, EMData *mask)
{
   // performs PCA on a list of images (each under a mask)
   // returns a list of eigenimages

   int i;

   vector<EMData*> img1dlst;
   vector<EMData*> eigvecs;
   vector<EMData*> eigenimages;

   int nimgs = imgstack.size();

   for (i=0; i<nimgs; i++) {
      img1dlst.push_back(Util::compress_image_mask(imgstack[i],mask));
   }

   // for right now, compute a full SVD
   eigvecs = Util::svdcmp(img1dlst, 0);

   img1dlst.clear();

   for (i=0; i<nimgs; i++) {
      eigenimages.push_back(Util::reconstitute_image_mask(eigvecs[i],mask));
   }

   eigvecs.clear();

   return eigenimages;
}

// return a subset of right singular vectors
vector <EMData*> PCA::dopca(vector <EMData*> imgstack, EMData *mask, int nvec)
{
   // performs PCA on a list of images (each under a mask)
   // returns a list of eigenimages

   vector<EMData*> img1dlst;
   vector<EMData*> eigvecs;
   vector<EMData*> eigenimages;

   int nimgs = imgstack.size();

   for (int i=0; i<nimgs; i++) {
      img1dlst.push_back(Util::compress_image_mask(imgstack[i],mask));
   }

   if ( nimgs < nvec || nvec == 0) nvec = nimgs;
   eigvecs = Util::svdcmp(img1dlst, nvec);
   img1dlst.clear();

   for (int i=0; i<nvec; i++) {
      eigenimages.push_back(Util::reconstitute_image_mask(eigvecs[i],mask));
   }

   eigvecs.clear();

   return eigenimages;
}

// PCA by Lanczos
#define qmat(i,j) qmat[((j)-1)*kstep + (i) -1]
#define diag(i)   diag[(i)-1]

vector <EMData*> PCA::dopca_lan(vector <EMData*> imgstack, EMData *mask, int nvec)
{
   // performs PCA on a list of images (each under a mask)
   // returns a list of eigenimages

   int ione = 1; 
   float one = 1.0, zero = 0.0;
   char trans;

   vector<EMData*> img1dlst;
   vector<EMData*> eigvecs;
   vector<EMData*> eigenimages;

   int status = 0;
   int nimgs = imgstack.size();
   for (int i=0; i<nimgs; i++) {
      img1dlst.push_back(Util::compress_image_mask(imgstack[i],mask));
   }

   float resnrm = 0.0;

   if ( nvec > nimgs || nvec ==0 ) nvec = nimgs;

   int nx = img1dlst[0]->get_xsize();
   // the definition of kstep is purely a heuristic for right now
   int kstep = nvec + 20;
   if (kstep > nimgs) kstep = nimgs;

   float *diag    = new float[kstep];
   float *subdiag = new float[kstep-1];
   float *vmat    = new float[nx*kstep];

   // run kstep-step Lanczos factorization
   status = Lanczos(img1dlst, &kstep, diag, subdiag, vmat, &resnrm);
/*
   for (int j = 0; j < kstep-1; j++)
      printf("subdiag(%d) = %11.3e\n", j, subdiag[j]);  
*/

   char jobz[2] = "V";
   float *qmat  = new float[kstep*kstep];
   // workspace size will be optimized later
   int   lwork  = 100 + 4*kstep + kstep*kstep;
   int   liwork = 3+5*kstep;

   float *work  = new float[lwork];
   int   *iwork = new int[liwork]; 
   int   info = 0;

   // call LAPACK tridiagonal eigensolver
   sstevd_(jobz, &kstep, diag, subdiag, qmat, &kstep, work, &lwork,
           iwork, &liwork, &info);

   // eigenvalues have been sorted in ascending order
   //for (int j = kstep; j > kstep - nvec; j--)
   //   printf("sigval2(%d) = %11.4e\n", j, sqrt(diag(j)));  

   img1dlst.clear();
   
   EMData *eigvec = new EMData();

   eigvec->set_size(nx, 1, 1);
   float *ritzvec = eigvec->get_data(); 

   // compute Ritz vectors (approximate eigenvectors) one at a time
   for (int j=0; j<nvec; j++) {
      trans = 'N';
      sgemv_(&trans, &nx, &kstep, &one, vmat, &nx, &qmat(1,kstep-j), &ione,
             &zero , ritzvec, &ione);  
      eigenimages.push_back(Util::reconstitute_image_mask(eigvec,mask));
   }

   eigvecs.clear();

   EMDeleteArray(diag);
   EMDeleteArray(subdiag);
   EMDeleteArray(vmat);
   EMDeleteArray(qmat);
   EMDeleteArray(work);
   EMDeleteArray(iwork);
   EMDeletePtr(eigvec);
   return eigenimages;
}
#undef diag
#undef qmat

// out of core version of PCA, not completed yet
char* PCA::dopca_ooc(const string &filename_in, EMData *mask, int nvec)
{
   char *filename_out = NULL;
   EMData *image_raw = new EMData();
   EMData *image_masked;

   int nimgs = EMUtil::get_image_count(filename_in);
   for (int i=0; i<nimgs; i++) {
       image_raw->read_image(filename_in, i);      
       image_masked=Util::compress_image_mask(image_raw,mask);
       image_masked->write_image("temp_masked_imaged.img",i); 
   }

   return filename_out;
}

#define TOL 1e-7
#define V(i,j)      V[((j)-1)*imgsize + (i) - 1]
#define T(i,j)      T[((j)-1)*(*kstep) + (i) - 1]
#define v0(i)       v0[(i)-1]
#define Av(i)       Av[(i)-1]
#define subdiag(i)  subdiag[(i)-1]
#define diag(i)     diag[(i)-1]
#define hvec(i)     hvec[(i)-1]

int PCA::Lanczos(vector <EMData*> imgstack, int *kstep, 
                 float  *diag, float *subdiag, float *V, 
                 float  *beta)
{
    /*
        Purpose: Compute a kstep-step Lanczos factorization
                 on the covariant matrix X*trans(X), where 
                 X (imgstack) contains a set of images;

        Input: 
           imgstack (vector <EMData*>) a set of images on which PCA is 
                                       to be performed;
           
           kstep (int*) The maximum number of Lanczos iterations allowed.
                          If Lanczos terminates before kstep steps
                          is reached (an invariant subspace is found), 
                          kstep returns the number of steps taken;
      
        Output:
           diag (float *) The projection of the covariant matrix into a
                          Krylov subspace of dimension at most kstep.
                          The projection is a tridiagonal matrix. The
                          diagonal elements of this matrix is stored in 
                          the diag array.

           subdiag (float*) The subdiagonal elements of the projection
                            is stored here.

           V (float *)    an imgsize by kstep array that contains a 
                          set of orthonormal Lanczos basis vectors;

           beta (float *) the residual norm of the factorization;
    */
    int i, j;
    
    float alpha;
    int   ione = 1;
    float zero = 0.0, one = 1.0, mone = -1.0;
    int   status = 0;
    
    char trans;
    int  nimgs = 0, imgsize = 0, ndim = 0; 
    float *v0, *Av, *hvec, *htmp, *imgdata;

    nimgs   = imgstack.size();
    if (nimgs <= 0) {
	status = 2; // no image in the stack
        goto EXIT; 
    }

    ndim = imgstack[0]->get_ndim();
    if (ndim != 1) {
        status = 3; // images should all be 1-d
        goto EXIT; 
    }

    imgsize = imgstack[0]->get_xsize();
     
    v0   = new float[imgsize];
    Av   = new float[imgsize];
    hvec = new float[*kstep];
    htmp = new float[*kstep];

    if (v0 == NULL || Av == NULL || hvec == NULL || htmp == NULL ) {
        fprintf(stderr, "Lanczos: failed to allocate v0,Av,hvec,htmp\n"); 
	status = -1;
        goto EXIT;
    }

    // may choose a random starting guess here     
    for ( i = 1; i <= imgsize; i++) v0(i) = 1.0;

    // normalize the starting vector
    *beta  = snrm2_(&imgsize, v0, &ione);
    for (i = 1; i<=imgsize; i++)
	V(i,1) = v0(i) / (*beta);

    // do Av <-- A*v0, where A is a cov matrix
    for (i = 0; i < nimgs; i++) {
       imgdata = imgstack[i]->get_data();
       alpha = sdot_(&imgsize, imgdata, &ione, V, &ione); 
       saxpy_(&imgsize, &alpha, imgdata, &ione, Av, &ione);
    }

    // Av <--- Av - V(:,1)*V(:,1)'*Av 
    diag(1) = sdot_(&imgsize, V, &ione, Av, &ione); 
    alpha   = -diag(1);
    saxpy_(&imgsize, &alpha, V, &ione, Av, &ione);

    // main loop 
    for ( j = 2 ; j <= *kstep ; j++ ) {
        *beta = snrm2_(&imgsize, Av, &ione);

        if (*beta < TOL) {
	    // found an invariant subspace, exit
            *kstep = j;
            break;
        }
 
        subdiag(j-1) = *beta;
	for ( i = 1 ; i <= imgsize ; i++ ) {
	    V(i,j) = Av(i) / (*beta);
	}	

        // do Av <-- A*V(:,j), where A is a cov matrix
        for (i = 0; i < imgsize; i++) Av[i] = 0;
        for (i = 0; i < nimgs; i++) {
           imgdata = imgstack[i]->get_data();
           alpha = sdot_(&imgsize, imgdata, &ione, &V(1,j), &ione); 
           saxpy_(&imgsize, &alpha, imgdata, &ione, Av, &ione);
        }
	
        // f <--- Av - V(:,1:j)*V(:,1:j)'*Av
        trans = 'T';
        status = sgemv_(&trans, &imgsize, &j, &one, V, &imgsize, Av, &ione,
                        &zero , hvec    , &ione); 
        trans = 'N';
        status = sgemv_(&trans, &imgsize, &j, &mone, V, &imgsize, hvec, 
                        &ione , &one    , Av, &ione);

        // one step of reorthogonalization
        trans = 'T';
        status = sgemv_(&trans, &imgsize, &j, &one, V, &imgsize, Av, &ione,
                        &zero , htmp    , &ione); 
        saxpy_(&j, &one, htmp, &ione, hvec, &ione); 
        trans = 'N';
        status = sgemv_(&trans, &imgsize, &j, &mone, V, &imgsize, htmp, 
                        &ione , &one    , Av, &ione);
        diag(j) = hvec(j);
    }

    EMDeleteArray(v0);
    EMDeleteArray(Av);
    EMDeleteArray(hvec);
    EMDeleteArray(htmp);

EXIT:
    return status;
}

#undef v0
#undef Av
#undef V
#undef T
