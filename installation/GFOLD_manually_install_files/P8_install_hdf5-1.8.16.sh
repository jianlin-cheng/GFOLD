#!/bin/bash -e

echo " Start compile hdf5-1.8.16 (will take ~1 min)"

cd /data/jh7x3/GFOLD/GFOLD_database_tools//tools

cd hdf5-1.8.16

./configure --with-zlib=/data/jh7x3/GFOLD/GFOLD_database_tools//tools/zlib-1.2.8

make

make install

echo "installed" > /data/jh7x3/GFOLD/GFOLD_database_tools//tools/hdf5-1.8.16/install.done

