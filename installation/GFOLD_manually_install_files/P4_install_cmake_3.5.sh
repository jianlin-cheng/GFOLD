#!/bin/bash -e

echo " Start compile cmake-3.5.2 (will take ~5 min)"

cd /data/commons/GFOLD_db_tools//tools

cd cmake-3.5.2

./bootstrap --prefix=/data/commons/GFOLD_db_tools//tools/cmake-3.5.2/

gmake

make DESTDIR=/data/commons/GFOLD_db_tools//cmake-3.5.2/ install

echo "installed" > /data/commons/GFOLD_db_tools//tools/cmake-3.5.2/install.done

