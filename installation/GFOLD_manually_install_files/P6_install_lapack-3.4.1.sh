#!/bin/bash -e

echo " Start compile lapack-3.4.1 (will take ~1 min)"

cd /data/commons/GFOLD_db_tools//tools

cd lapack-3.4.1

cp make.inc.example make.inc

make blaslib  # To generate the Reference BLAS Library

make

echo "installed" > /data/commons/GFOLD_db_tools//tools/lapack-3.4.1/install.done

