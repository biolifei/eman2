#!/usr/bin/env bash

set -xe

e2version.py
e2speedtest.py

python "${SRC_DIR}/tests/test_EMAN2DIR.py"

bash "${SRC_DIR}/tests/run_prog_tests.sh"
