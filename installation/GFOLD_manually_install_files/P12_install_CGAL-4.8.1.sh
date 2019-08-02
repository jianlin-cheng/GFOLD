#!/bin/bash -e

echo " Start compile CGAL-4.8.1 (will take ~1 min)"

cd /data/commons/GFOLD_db_tools//tools

cd CGAL-4.8.1

export PATH=/data/commons/GFOLD_db_tools//tools/cmake-2.8.12.2/bin/:$PATH

export PATH=/data/commons/GFOLD_db_tools//tools/gmp-4.3.2/:$PATH

export PATH=/data/commons/GFOLD_db_tools//tools/mpfr-2.4.2/:$PATH

export BOOST_ROOT="/data/commons/GFOLD_db_tools//tools/boost_1_55_0"

export BOOST_INCLUDE="/data/commons/GFOLD_db_tools//tools/boost_1_55_0/include"

export BOOST_LIBDIR="/data/commons/GFOLD_db_tools//tools/boost_1_55_0/lib"

export BOOST_OPTS="-DBOOST_ROOT=${BOOST_ROOT} -DBOOST_INCLUDEDIR=${BOOST_INCLUDE} -DBOOST_LIBRARYDIR=${BOOST_LIBDIR}"

cmake .

make

echo "installed" > /data/commons/GFOLD_db_tools//tools/CGAL-4.8.1/install.done

