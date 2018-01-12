#!/bin/bash

set -xe

unset MACOSX_DEPLOYMENT_TARGET

build_dir="${SRC_DIR}/../build_eman"

rm -rf $build_dir
mkdir -p $build_dir
cd $build_dir

cmake $SRC_DIR

make -j${CPU_COUNT}
make install
make test-verbose
