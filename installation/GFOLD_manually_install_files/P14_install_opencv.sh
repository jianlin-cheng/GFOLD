#!/bin/bash -e

echo " Start compile opencv (will take ~10 min)"

cd /data/jh7x3/GFOLD/GFOLD_database_tools//tools

cd opencv

mkdir /data/jh7x3/GFOLD/GFOLD_database_tools//tools/opencv/release

cd /data/jh7x3/GFOLD/GFOLD_database_tools//tools/opencv/release

/data/jh7x3/GFOLD/GFOLD_database_tools//tools/cmake-3.5.2/bin/cmake -D CMAKE_BUILD_TYPE=RELEASE -D  CMAKE_INSTALL_PREFIX=/data/jh7x3/GFOLD/GFOLD_database_tools//tools/opencv/release ..

make -j 8

#make install

echo "installed" > /data/jh7x3/GFOLD/GFOLD_database_tools//tools/opencv/install.done

