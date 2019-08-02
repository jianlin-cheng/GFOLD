#!/bin/bash -e

echo " Start compile fftw-3.3.4 (will take ~1 min)"

cd /data/jh7x3/GFOLD/GFOLD_database_tools//tools

cd fftw-3.3.4

./configure --prefix=/data/jh7x3/GFOLD/GFOLD_database_tools//tools/fftw-3.3.4/ --enable-shared  --with-pic

make

make install

echo "installed" > /data/jh7x3/GFOLD/GFOLD_database_tools//tools/fftw-3.3.4/install.done

