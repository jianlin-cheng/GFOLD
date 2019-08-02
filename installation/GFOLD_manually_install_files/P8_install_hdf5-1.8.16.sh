#!/bin/bash -e

echo " Start compile hdf5-1.8.16 (will take ~1 min)"

cd /data/commons/GFOLD_db_tools//tools

cd hdf5-1.8.16

./configure --with-zlib=/data/commons/GFOLD_db_tools//tools/zlib-1.2.8

make

make install

echo "installed" > /data/commons/GFOLD_db_tools//tools/hdf5-1.8.16/install.done

