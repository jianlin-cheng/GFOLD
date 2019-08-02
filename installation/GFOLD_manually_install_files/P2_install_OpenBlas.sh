#!/bin/bash -e

echo " Start compile OpenBlas (will take ~5 min)"

cd /data/commons/GFOLD_db_tools//tools

cd OpenBLAS

#make clean

make

make PREFIX=/data/commons/GFOLD_db_tools//tools/OpenBLAS install

echo "installed" > /data/commons/GFOLD_db_tools//tools/OpenBLAS/install.done

