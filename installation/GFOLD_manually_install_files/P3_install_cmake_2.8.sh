#!/bin/bash -e

echo " Start compile cmake-2.8 (will take ~5 min)"

cd /data/commons/GFOLD_db_tools//tools

cd cmake-2.8.12.2/

./bootstrap --prefix=/data/commons/GFOLD_db_tools//tools/cmake-2.8.12.2/

gmake

make DESTDIR=/data/commons/GFOLD_db_tools//cmake-2.8.12.2/ install

echo "installed" > /data/commons/GFOLD_db_tools//tools/cmake-2.8.12.2//install.done

