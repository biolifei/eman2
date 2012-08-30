#!/usr/bin/env python

'''
====================
Author: Jesus Galaz - 2011, Last update: 02/2011
====================

# This software is issued under a joint BSD/GNU license. You may use the
# source code in this file under either license. However, note that the
# complete EMAN2 and SPARX software packages have some GPL dependencies,
# so you are responsible for compliance with the licenses of these packages
# if you opt to use BSD licensing. The warranty disclaimer below holds
# in either instance.
#
# This complete copyright notice must be included in any revised version of the
# source code. Additional authorship citations may be added, but existing
# author citations must be preserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  2111-1307 USA
'''

from optparse import OptionParser
from EMAN2 import *
from sys import argv
import EMAN2
import heapq
import operator
import random
import numpy

def main():
	progname = os.path.basename(sys.argv[0])
	usage = """%prog [options]

	This program produces simulated sub volumes in random orientations from a given PDB or EM file. The output is ALWAYS in HDF format, since it's the only format supported by E2SPT programs.
	"""
			
	parser = EMArgumentParser(usage=usage,version=EMANVERSION)	
	
	parser.add_argument("--path",type=str,default=None,help="Directory to store results in. The default is a numbered series of directories containing the prefix 'sptsim'; for example, sptsim_02 will be the directory by default if 'sptsim_01' already exists.")
	parser.add_argument("--output",type=str,default=None,help="Name of the output stack for the simulated subtomograms.")

	parser.add_argument("--input", type=str, help="""The name of the input volume from which simulated subtomograms will be generated. 
							The output will be in HDF format, since volume stack support is required. The input CAN be PDB, MRC or and HDF stack. 
							If the input file is PDB or MRC, a version of the supplied model will be written out in HDF format.
							If the input file is a stack, simulatd subvolumes will be generated from each model in the stack and written to different output stacks.
							For example, if the input file contains models A and B, two output stacks with simulated subvolumes will be generated.""", default=None)
				
	parser.add_argument("--filter",type=str,help="""A filter (as in a processor from e2proc3d.py) apply to the model before generating simulated particles from it.
							Type 'e2help.py processors' at the command line and find the options availbale from the processors list)""",default=None)
	
	parser.add_argument("--shrink", type=int,default=1,help="Optionally shrink the input volume before the simulation if you want binned/down-sampled subtomograms.")
	parser.add_argument("--verbose", "-v", type=int, dest="verbose", action="store", metavar="n", default=0, help="verbose level [0-9], higner number means higher level of verboseness")
	
	parser.add_argument("--nptcls", type=int,default=10,help="Number of simulated subtomograms tu generate per referece.")
	parser.add_argument("--txrange", type=int,default=None,help="""Maximum number of pixels to randomly translate each subtomogram in X. The random translation will be picked between -txrange and +txrange. 
								     Default value is set by --transrange, but --txrange will overwrite it if specified.""")
	parser.add_argument("--tyrange", type=int,default=None,help="""Maximum number of pixels to randomly translate each subtomogram in Y. The random translation will be picked between -tyrange and +tyrange.
								     Default value is set by --transrange, but --txrange will overwrite it if specified.""")
	parser.add_argument("--tzrange", type=int,default=None,help="""Maximum number of pixels to randomly translate each subtomogram in Z. The random translation will be picked between -tzrange and +tzrange.
								     Default value is set by --transrange, but --txrange will overwrite it if specified.""")
	parser.add_argument("--transrange", type=int,default=4,help="""Maximum number of pixels to randomly translate each subtomogram in all X, Y and Z. 
									The random translation will be picked between -transrage and +transrange; --txrange, --tyrange and --tzrange overwrite --transrange for each specified direction.""")
	
	parser.add_argument("--tiltstep", type=int,default=5,help="Degrees between each image in the simulated tilt series for each subtomogram.")
	parser.add_argument("--tiltrange", type=int,default=60,help="""Maximum angular value at which the highest tilt picture will be simulated. Projections will be simulated from -tiltrange to +titlrange. 
									For example, if simulating a tilt series collected from -60 to 60 degrees, enter a --tiltrange value of 60. 
									Note that this parameter will determine the size of the missing wedge.""")
	parser.add_argument("--applyctf", action="store_true",default=False,help="If on, it applies ctf to the projections in the simulated tilt series based on defocus, cs, and voltage parameters.")
	
	parser.add_argument("--orthogonal", action="store_true",default=False,help="If on, --nptcls is ignored and you get 3 subtomograms (simulated from the model supplied) which are orthogonal to each other.")

	parser.add_argument("--defocus", type=int,default=3,help="Intended defocus at the tilt axis (in microns) for the simulated tilt series.")
	parser.add_argument("--voltage", type=int,default=200,help="Voltage of the microscope, used to simulate the ctf added to the subtomograms.")
	parser.add_argument("--cs", type=int,default=2,help="Cs of the microscope, used to simulate the ctf added to the subtomograms.")

	parser.add_argument("--gridholesize", type=int,default=2,help="""Size of the carbon hole for the simulated grid (this will determine shifts in defocus for each particle at 
									each tilt step, depending on the position of the particle respect to the tilt axis, which is assigned randomly.""")
	parser.add_argument("--saverandstack", action="store_true",default=False,help="Save the stack of randomly oriented particles, before subtomogram simulation (before the missing wedge and noise are added).")
	parser.add_argument("--saveprjs", action="store_true",default=False,help="Save the projections (the 'tilt series') for each simulated subtomogram.")

	parser.add_argument("--reconstructor", type=str,default="fourier",help="""The reconstructor to use to reconstruct the tilt series into a tomogram. Type 'e2help.py reconstructors' at the command line
											to see all options and parameters available.""")
	parser.add_argument("--pad", type=int,default=0,help="""If on, it will increase the box size of the model BEFORE generating projections and doing 3D reconstruction of simulated sutomograms.""")								
	#parser.add_argument("--noiseproc",type=str,help="A noise processor to be applied to the individual projections of the simulated tilt series",default=None)
	
	parser.add_argument("--finalboxsize", type=int,default=0,help="""The final box size to clip the subtomograms to.""")								

	parser.add_argument("--snr",type=int,help="Weighing noise factor for noise added to the image. Only words if --addnoise is on.",default=0)
	parser.add_argument("--addnoise",action="store_true",default=False,help="If on, it adds random noise to the particles")
	
	parser.add_argument("--sym",type=str,default='c1',help="If your particle is symmetrical, you should randomize it's orientation withing the asymmetric unit only. Thus, provide the symmetry.")

	parser.add_argument("--notrandomize",action="store_true",default=False,help="This will prevent the simulated particles from being rotated and translated into random orientations.")
	parser.add_argument("--simref",action="store_true",default=False,help="This will make a simulated particle in the same orientation as the original input (or reference).")
	parser.add_argument("--negativecontrast",action="store_true",default=False,help="This will make the simulated particles be like real EM data before contrast reversal. Otherwise, 'white protein' (positive density values) will be used.")

	parser.add_argument("--ppid", type=int, help="Set the PID of the parent process, used for cross platform PPID",default=-1)

	(options, args) = parser.parse_args()	
	
	logger = E2init(sys.argv, options.ppid)

	'''
	Make the directory where to create the database where the results will be stored
	'''
	
	#if options.path and ("/" in options.path or "#" in options.path) :
	#	print "Path specifier should be the name of a subdirectory to use in the current directory. Neither '/' or '#' can be included. "
	#	sys.exit(1)
		
	#if options.path and options.path[:4].lower()!="bdb:": 
	#	options.path="bdb:"+options.path

	#if not options.path: 
	#	#options.path="bdb:"+numbered_path("sptavsa",True)
	#	options.path = "sptsim_01"
	
	
	if options.path and ("/" in options.path or "#" in options.path) :
		print "Path specifier should be the name of a subdirectory to use in the current directory. Neither '/' or '#' can be included. "
		sys.exit(1)

	if not options.path: 
		#options.path="bdb:"+numbered_path("sptavsa",True)
		options.path = "sptsim_01"
	
	files=os.listdir(os.getcwd())
	print "right before while loop"
	while options.path in files:
		print "in while loop making path in e2spt_simulation.py, options.path is", options.path
		#path = options.path
		if '_' not in options.path:
			print "I will add the number"
			options.path = options.path + '_00'
		else:
			jobtag=''
			components=options.path.split('_')
			if components[-1].isdigit():
				components[-1] = str(int(components[-1])+1).zfill(2)
			else:
				components.append('00')
						
			options.path = '_'.join(components)
			#options.path = path
			print "The new options.path is", options.path

	if options.path not in files:
		
		print "I will make the path", options.path
		os.system('mkdir ' + options.path)
	
	
	'''
	Parse the options
	'''
	if options.filter:
		options.filter = parsemodopt(options.filter)
		
	#if options.noiseproc:
	#	options.noiseproc= parsemodopt(options.noiseproc)
		
	if options.reconstructor:
		options.reconstructor= parsemodopt(options.reconstructor)
	
	
	'''
	If PDB or MRC files are provided to similuate subtomograms, convert them to HDF
	'''
	
	check=0
	if '.pdb' in options.input:
		pdbmodel = options.input
		os.system('cp ' + pdbmodel + ' ' + options.path)
		pdbmodel = options.path + '/' + pdbmodel.split('/')[-1]
		mrcmodel = pdbmodel.replace('.pdb','.mrc')
		os.system('e2pdb2mrc.py ' + pdbmodel + ' ' + mrcmodel + ' && rm ' + pdbmodel)
		options.input = mrcmodel
		check=1
	
	if '.mrc' in options.input:
		mrcmodel = options.input
		if check==0:
			os.system('cp ' + mrcmodel + ' ' + options.path)
			mrcmodel = options.path + '/' + mrcmodel.split('/')[-1]
		hdfmodel = mrcmodel.replace('.mrc','.hdf')
		os.system('e2proc3d.py ' + options.input + ' ' + hdfmodel + ' && rm ' + mrcmodel)
		options.input = hdfmodel
		check=1
	
	nrefs = EMUtil.get_image_count(options.input)
	
	if '.hdf' in options.input:
		hdfmodel = options.input
		if check == 0:
			os.system('cp ' + hdfmodel + ' ' + options.path)
			hdfmodel = options.path + '/' + hdfmodel.split('/')[-1]
			options.input = hdfmodel
		workname = hdfmodel.replace('.hdf','_sptsimMODEL.hdf')
		if nrefs > 1:
			workname = hdfmodel.replace('.hdf','_sptsimMODELS.hdf')
		
		os.system('cp ' + hdfmodel + ' ' + workname + ' && rm ' + hdfmodel)
		options.input = workname
	
	tag = ''
	
	originalpath = options.path
	for i in range(nrefs):
		if nrefs>1:
			modelfilename = options.input.split('/')[-1].replace('.hdf','_model' + str(i).zfill(2) + '.hdf')
			options.path = originalpath + '/model' + str(i).zfill(2)
			os.system('mkdir ' + options.path)
			#cmd = 'e2proc3d.py '  + options.input + ' ' + options.path + '/' + modelfilename + ' --first=' + str(i) + ' --last=' + str(i) + ' --append'
			os.system('e2proc3d.py '  + options.input + ' ' + options.path + '/' + modelfilename + ' --first=' + str(i) + ' --last=' + str(i) + ' --append')
			#print "This is the command to create the model", cmd
			options.input = options.path + '/' + modelfilename
			#print "Therefore, the model to load is", options.input
		
		randptcls = []
		if nrefs > 1:
			tag = str(i).zfill(len(str(nrefs)))
	
		model = EMData(options.input,0,True)
		#print "The apix of the model is", model['apix_x']
		
		newsize = model['nx']
		oldx = model['nx']
	
		if model['nx'] != model['ny'] or model['nx'] != model['nz'] or model['ny'] != model['nz']:
			newsize = max(model['nx'], model['ny'], model['nz'])
			
		if options.shrink != None and options.shrink > 1:
			newsize = newsize/options.shrink	
			if newsize % 2:
				newsize += 1
			
			os.system('e2proc3d.py ' + options.input + ' ' + options.input + ' --process=math.meanshrink:n=' + str(options.shrink))
	
		padded=options.input
		if options.pad:
			newsize *= options.pad
			#padded=padded.replace('.hdf','_padded.hdf')
							
		if newsize != oldx:
			os.system('e2proc3d.py ' + options.input + ' ' + options.input + ' --clip=' + str(newsize) + ' --first=' + str(i) + ' --last=' + str(i))	
			options.input=padded
			
		model = EMData(options.input,0)
		#print "after editing, apix of model is", model['apix_x']

		if options.filter != None:
			model.process_inplace(options.filter[0],options.filter[1])
		
		model.process_inplace('normalize')
		model['origin_x'] = 0									#Make sure the origin is set to zero, to avoid display issues with Chimera
		model['origin_y'] = 0
		model['origin_z'] = 0

		stackname = options.input.replace('.hdf','_randst' + tag + '_n' + str(options.nptcls).zfill(len(str(options.nptcls))) + '.hdf').split('/')[-1]
		if options.output:
			stackname = options.output

		randptcls = randomizer(options, model, stackname)
		
		#stackname = options.input.replace('.hdf','_randst' + tag + '_n' + str(options.nptcls).zfill(len(str(options.nptcls))) + '.hdf')
		
		if options.output:
			stackname = options.output
		
		ret=subtomosim(options,randptcls, stackname)
		if ret == 1:
			os.system('e2proc3d.py ' + options.input + ' ' + options.input + ' --clip=' + str(options.finalboxsize) + ' --first=' + str(i) + ' --last=' + str(i))	
		
		if options.simref:
			name = options.input.replace('.hdf','_SIM.hdf')
			model['sptsim_randT'] = Transform()
			model['xform.align3d'] = Transform()
			ret = subtomosim(options,[model],name)
			
			if ret == 1:
				os.system('e2proc3d.py ' + name + ' ' + name + ' --clip=' + str(options.finalboxsize) + ' --first=' + str(i) + ' --last=' + str(i))	
	
	E2end(logger)
					
	return()
	

'''
====================
RANDOMIZER - Takes a file in .hdf format and generates a set of n particles randomly rotated and translated, where n is
the size of the set and is defined by the user
====================
'''
def randomizer(options, model, stackname):
	
	print "I am inside the RANDOMIZER"
	
	if options.verbose:
		print "You have requested to generate %d particles with random orientations and translations" %(options.nptcls)
	
	randptcls = []
	
	if options.orthogonal:
		for i in range(3):
			b = model.copy()
			
			if i==0:
				randptcls.append(b)

			if i == 1:
				b.rotate(0,90,0)
				randptcls.append(b)
			if i == 2:
				b.rotate(0,90,90)
				randptcls.append(b)
			
	else:	
		for i in range(options.nptcls):
			if options.verbose:
				print "I will generate particle #", i

			b = model.copy()
			
			random_transform = Transform()	
			if not options.notrandomize:
				rand_orient = OrientGens.get("rand",{"n":1, "phitoo":1})				#Generate a random orientation (randomizes all 3 euler angles)
				c1_sym = Symmetries.get("c1")
				random_transform = rand_orient.gen_orientations(c1_sym)[0]

				randtx = random.randrange(-1 * options.transrange, options.transrange)			#Generate random translations
				randty = random.randrange(-1 * options.transrange, options.transrange)
				randtz = random.randrange(-1 * options.transrange, options.transrange)

				if options.txrange:
					randtx = random.randrange(-1 * options.txrange, options.txrange)	
				if options.tyrange:
					randty = random.randrange(-1 * options.tyrange, options.tyrange)
				if options.tzrange:
					randtz = random.randrange(-1 * options.tzrange, options.tzrange)

				random_transform.translate(randtx, randty, randtz)

				b.transform(random_transform)		

			b['sptsim_randT'] = random_transform
			b['xform.align3d'] = Transform()							#This parameter should be set to the identity transform since it can be used later to determine whether
														#alignment programs can "undo" the random rotation in spt_randT accurately or not
			if options.saverandstack:	
				
				print "The stackname to use is", stackname
				b.write_image(options.path + '/' + stackname.split('/')[-1],i)

			randptcls.append(b)

			if options.verbose:
				print "The random transform applied to it was", random_transform

	return(randptcls)
	
'''
====================
SUBTOMOSIM takes a set of particles in .hdf format and generates a simulated sub-tomogram for each, using user-defined parameters for tomographic simulation.
The function generates projections for each particle with a user-defined tilt step and missing wedge size (or data collection range),
adds noise and ctf to each projection, randomizes the position of each particle "in the ice" and changes the defocus for each picture in the tilt series accordingly,
and recounstructs a new 3D volume from the simulated tilt series.
====================
'''	
def subtomosim(options,ptcls,stackname):

	lower_bound = -1 * options.tiltrange
	upper_bound = options.tiltrange
	
	nslices = int(round((upper_bound - lower_bound)/ options.tiltstep))
	
	if options.verbose:
		print "There are these many particles in the set", len(ptcls)
		print "And these many slices to simulate each subtomogram", nslices
	
	outname = stackname.replace('.hdf','_ptcls.hdf')
	
	if len(ptcls) == 1 and '_SIM.hdf' in stackname:
		outname = stackname.split('/')[-1]
	
	for i in range(len(ptcls)):
		if options.verbose:
			print "Projecting and adding noise to particle #", i

		apix = ptcls[i]['apix_x']
		
		px = random.uniform(-1* options.gridholesize/2, options.gridholesize/2)			#random distance of the particle's center from the tilt axis
			
		alt = lower_bound
		raw_projections = []
		ctfed_projections = []
		
		randT = ptcls[i]['sptsim_randT']
		
		for j in range(nslices):
			t = Transform({'type':'eman','az':0,'alt':alt,'phi':0})				#Generate the projection orientation for each picture in the tilt series
			
			dz = -1 * px * numpy.sin(alt)							#Calculate the defocus shift per picture, per particle, depending on the 
													#particle's position relative to the tilt axis. For particles left of the tilt axis,
													#px is negative. With negative alt [left end of the ice down, right end up], 
													#dz should be negative.
			defocus = options.defocus + dz
						
			prj = ptcls[i].project("standard",t)
			prj.set_attr('xform.projection',t)
			prj['apix_x']=apix
			prj['apix_y']=apix
			
			#print "The size of the prj is", prj['nx']
			
			prj.process_inplace('normalize')
			
			if options.saveprjs:
				prj.write_image( options.path + '/' + stackname.replace('.hdf', '_ptcl' + str(i).zfill(len(str(nslices))) + '_prjsRAW.hdf') , j)					#Write projections stack for particle i
			raw_projections.append(prj)
					
			prj_fft = prj.do_fft()
			
			if options.negativecontrast:
				prj_fft.mult(-1)								#Reverse the contrast, as in "authentic" cryoEM data		
			
			if options.applyctf:
				ctf = EMAN2Ctf()
				ctf.from_dict({'defocus':options.defocus,'bfactor':100,'ampcont':0.05,'apix':apix,'voltage':options.voltage,'cs':options.cs})	
				prj_ctf = prj_fft.copy()	
				ctf.compute_2d_complex(prj_ctf,Ctf.CtfType.CTF_AMP)
				prj_fft.mult(prj_ctf)
			
			prj_r = prj_fft.do_ift()							#Go back to real space
			
			if options.addnoise and options.snr:
				#prj_r.process_inplace('math.addnoise',{'noise':options.snr})
				
				#prj_n = EMData(nx,ny)
				#for i in range(options.snr):				
				#	prj_n.process_inplace(options.noiseproc[0],options.noiseproc[1])
				#	prj_r = prj_r + prj_n
				#prj_n.write_image('NOISE_ptcl' + str(i).zfill(len(str(nslices))) + '.hdf',j)
				
				nx=prj_r['nx']
				ny=prj_r['ny']
				
		 		noise = test_image(1,size=(nx,ny))
	                        noise2 = noise.process("filter.lowpass.gauss",{"cutoff_abs":.25})
	                        noise.process_inplace("filter.lowpass.gauss",{"cutoff_abs":.75})
	                        noise = ( noise*3 + noise2*3 ) * options.snr
	                        prj_r.add(noise)

			ctfed_projections.append(prj_r)		

			if options.saveprjs and options.applyctf or options.saveprjs and options.addnoise:
				prj_r.write_image(options.path + '/' + stackname.replace('.hdf', '_ptcl' + str(i).zfill(len(str(nslices))) + '_prjsEDITED.hdf') , j)	
			
						
			alt += int(options.tiltstep)
		
		box = ptcls[i].get_xsize()
		
		if options.finalboxsize:
			box = options.finalboxsize
		
		r = Reconstructors.get(options.reconstructor[0],{'size':(box,box,box),'sym':'c1','verbose':True,'mode':'gauss_2'})
		#r = Reconstructors.get(options.reconstructor[0],options.reconstructor[1])
		r.setup()
		
		for p in ctfed_projections:
			#print "The size of the prj to insert is", p['nx']
			p = r.preprocess_slice(p,p['xform.projection'])
			r.insert_slice(p,p['xform.projection'],1.0)
		
		rec = r.finish(True)
		#mname = parameters['model'].split('/')[-1].split('.')[0]
		#name = 'rec_' + mname + '#' + str(i).zfill(len(str(len(particles)))) + '.hdf'
		
		rec['apix_x']=apix
		rec['apix_y']=apix
		rec['apix_z']=apix
		rec['sptsim_randT'] = randT
		
		#print "The apix of rec is", rec['apix_x']
		rec.write_image(options.path + '/' + outname,i)
	
	
	return(1)	

if __name__ == '__main__':
	main()
