#!/bin/bash -e

echo " Start compile cmake-3.5.2 (will take ~5 min)"

cd /data/jh7x3/GFOLD/GFOLD_database_tools//tools

cd cmake-3.5.2

./bootstrap --prefix=/data/jh7x3/GFOLD/GFOLD_database_tools//tools/cmake-3.5.2/

gmake

make DESTDIR=/data/jh7x3/GFOLD/GFOLD_database_tools//cmake-3.5.2/ install

echo "installed" > /data/jh7x3/GFOLD/GFOLD_database_tools//tools/cmake-3.5.2/install.done

