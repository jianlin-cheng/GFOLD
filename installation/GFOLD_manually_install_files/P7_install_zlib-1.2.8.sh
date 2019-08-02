#!/bin/bash -e

echo " Start compile zlib-1.2.8 (will take ~1 min)"

cd /data/commons/GFOLD_db_tools//tools

cd zlib-1.2.8

./configure  --prefix=/data/commons/GFOLD_db_tools//tools/zlib-1.2.8

make

make install

echo "installed" > /data/commons/GFOLD_db_tools//tools/zlib-1.2.8/install.done

