#!/bin/bash -e

echo " Start compile OpenBlas (will take ~5 min)"

cd /data/jh7x3/GFOLD/GFOLD_database_tools//tools

cd OpenBLAS

#make clean

make

make PREFIX=/data/jh7x3/GFOLD/GFOLD_database_tools//tools/OpenBLAS install

echo "installed" > /data/jh7x3/GFOLD/GFOLD_database_tools//tools/OpenBLAS/install.done

