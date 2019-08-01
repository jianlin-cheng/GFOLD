#!/bin/bash -e

echo " Start compile gmp-4.3.2 (will take ~1 min)"

cd /data/jh7x3/GFOLD/GFOLD_database_tools//tools

cd gmp-4.3.2

./configure --prefix=/data/jh7x3/GFOLD/GFOLD_database_tools//tools/gmp-4.3.2

make

make install

echo "installed" > /data/jh7x3/GFOLD/GFOLD_database_tools//tools/gmp-4.3.2/install.done

