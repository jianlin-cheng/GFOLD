#!/bin/bash -e

echo " Start compile opencv (will take ~10 min)"

cd /data/commons/GFOLD_db_tools//tools

cd opencv

mkdir /data/commons/GFOLD_db_tools//tools/opencv/release

cd /data/commons/GFOLD_db_tools//tools/opencv/release

/data/commons/GFOLD_db_tools//tools/cmake-3.5.2/bin/cmake -D CMAKE_BUILD_TYPE=RELEASE -D  CMAKE_INSTALL_PREFIX=/data/commons/GFOLD_db_tools//tools/opencv/release ..

make -j 8

#make install

echo "installed" > /data/commons/GFOLD_db_tools//tools/opencv/install.done

