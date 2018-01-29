#!/usr/bin/env bash

if [ ! -z ${CI} ];then
    source ci_support/setup_conda.sh

    # Following Wiki instructions at
    # http://blake.bcm.edu/emanwiki/EMAN2/COMPILE_EMAN2_ANACONDA
    if [ "$(uname -s)" != "Darwin" ];then
        conda install --yes --quiet eman-deps="*"="np19*" -c cryoem -c defaults -c conda-forge
    else
        conda install --yes --quiet eman-deps -c cryoem -c defaults -c conda-forge
    fi
fi

# Build and install eman2
export CPU_COUNT=2

export SRC_DIR=${PWD}
export PREFIX=${PWD}
bash ${SRC_DIR}/recipes/eman/build.sh

# Run tests
bash ${SRC_DIR}/tests/run_tests.sh
