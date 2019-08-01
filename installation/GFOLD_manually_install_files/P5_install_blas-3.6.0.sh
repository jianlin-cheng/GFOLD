#!/bin/bash -e

echo " Start compile blas-3.6.0 (will take ~1 min)"

cd /data/jh7x3/GFOLD/GFOLD_database_tools//tools

cd blas-3.6.0

make

mv blas_LINUX.a libblas.a

echo "installed" > /data/jh7x3/GFOLD/GFOLD_database_tools//tools/blas-3.6.0/install.done

