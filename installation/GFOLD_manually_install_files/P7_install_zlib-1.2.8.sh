#!/bin/bash -e

echo " Start compile zlib-1.2.8 (will take ~1 min)"

cd /data/jh7x3/GFOLD/GFOLD_database_tools//tools

cd zlib-1.2.8

./configure  --prefix=/data/jh7x3/GFOLD/GFOLD_database_tools//tools/zlib-1.2.8

make

make install

echo "installed" > /data/jh7x3/GFOLD/GFOLD_database_tools//tools/zlib-1.2.8/install.done

