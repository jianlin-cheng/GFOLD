#!/bin/bash -e

echo " Start compile gsl-2.1 (will take ~1 min)"

cd /data/jh7x3/GFOLD/GFOLD_database_tools//tools

cd gsl-2.1

./configure --prefix=/data/jh7x3/GFOLD/GFOLD_database_tools//tools/gsl-2.1

make

make install

echo "installed" > /data/jh7x3/GFOLD/GFOLD_database_tools//tools/gsl-2.1/install.done

