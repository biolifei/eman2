#ifndef eman__gatan2io_h__
#define eman__gatan2io_h__ 1

#include "imageio.h"
#include <stdio.h>

namespace EMAN {

    class Gatan2IO: public ImageIO {
    public:
	Gatan2IO(string filename, IOMode rw_mode = READ_ONLY);
	~Gatan2IO();
	
	DEFINE_IMAGEIO_FUNC;
    private:
	enum DataType {
	    GATAN2_SHORT = 1,
	    GATAN2_FLOAT = 2,
	    GATAN2_COMPLEX = 3,
	    GATAN2_PACKED_COMPLEX = 5,
	    GATAN2_CHAR = 6,
	    GATAN2_LONG = 7,
	    GATAN2_INVALID
	};
	
	struct Gatan2Header {
	    short version;
	    short un1;
	    short un2;
	    short nx;
	    short ny;
	    short len;	
	    short type;
	};

	int to_em_datatype(int gatan_type);
	
    private:
	string filename;
	IOMode rw_mode;
	FILE* gatan2_file;
	Gatan2Header gatanh;
	
	bool is_big_endian;
	bool initialized;
    };
    
}


#endif
