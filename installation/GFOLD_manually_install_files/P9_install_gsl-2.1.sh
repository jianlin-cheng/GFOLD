#!/bin/bash -e

echo " Start compile gsl-2.1 (will take ~1 min)"

cd /data/commons/GFOLD_db_tools//tools

cd gsl-2.1

./configure --prefix=/data/commons/GFOLD_db_tools//tools/gsl-2.1

make

make install

echo "installed" > /data/commons/GFOLD_db_tools//tools/gsl-2.1/install.done

