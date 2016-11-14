# Cygwin 32 on Windows 7
export TARGET="i686-pc-mingw32"
export BROOT="/build"
export PREFIX="${BROOT}/local"

# PATHS
export PATH=${PREFIX}/bin:${PREFIX}/python:${PATH}
export PKG_CONFIG_PATH=${PREFIX}/lib/pkgconfig:${PREFIX}/python/lib/pkgconfig:${PKG_CONFIG_PATH}
export CMAKE_PREFIX_PATH=${PREFIX}
export PYTHONPATH=${PREFIX}/site-packages:${PYTHONPATH}

# Configure and compile flags
export CFLAGS="-O2 -g -I${PREFIX}/include -I${PREFIX}/python/include"
export CXXFLAGS=$CFLAGS
export LDFLAGS="-L${PREFIX}/lib -L${PREFIX}/python/libs"
