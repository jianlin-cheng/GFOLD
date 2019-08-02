#!/bin/bash -e

echo " Start compile mpfr-2.4.2 (will take ~1 min)"

cd /data/commons/GFOLD_db_tools//tools

cd mpfr-2.4.2

./configure --prefix=/data/commons/GFOLD_db_tools//tools/mpfr-2.4.2/ --enable-static --disable-shared  --with-gmp-build=/data/commons/GFOLD_db_tools//tools/gmp-4.3.2

make

make install

echo "installed" > /data/commons/GFOLD_db_tools//tools/mpfr-2.4.2/install.done

