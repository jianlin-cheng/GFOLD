#!/bin/bash -e

echo " Start compile lapack-3.4.1 (will take ~1 min)"

cd /data/jh7x3/GFOLD/GFOLD_database_tools//tools

cd lapack-3.4.1

cp make.inc.example make.inc

make blaslib  # To generate the Reference BLAS Library

make

echo "installed" > /data/jh7x3/GFOLD/GFOLD_database_tools//tools/lapack-3.4.1/install.done

