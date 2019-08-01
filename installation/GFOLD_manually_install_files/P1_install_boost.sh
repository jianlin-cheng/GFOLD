#!/bin/bash -e

echo " Start compile boost (will take ~20 min)"

cd /data/jh7x3/GFOLD/GFOLD_database_tools//tools

cd boost_1_55_0

./bootstrap.sh  --prefix=/data/jh7x3/GFOLD/GFOLD_database_tools//tools/boost_1_55_0

./b2

./b2 install

echo "installed" > /data/jh7x3/GFOLD/GFOLD_database_tools//tools/boost_1_55_0/install.done

