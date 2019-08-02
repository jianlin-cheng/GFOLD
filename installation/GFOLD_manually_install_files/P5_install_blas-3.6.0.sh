#!/bin/bash -e

echo " Start compile blas-3.6.0 (will take ~1 min)"

cd /data/commons/GFOLD_db_tools//tools

cd blas-3.6.0

make

mv blas_LINUX.a libblas.a

echo "installed" > /data/commons/GFOLD_db_tools//tools/blas-3.6.0/install.done

