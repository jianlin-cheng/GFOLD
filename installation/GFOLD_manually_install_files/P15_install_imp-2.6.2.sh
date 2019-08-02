#!/bin/bash -e

echo " Start compile imp-2.6.2 (will take ~10 min)"

cd /data/jh7x3/GFOLD/GFOLD_database_tools//tools

cd imp-2.6.2

export PATH=/data/jh7x3/GFOLD/GFOLD_database_tools//tools/boost_1_55_0/:$PATH
export PATH=/data/jh7x3/GFOLD/GFOLD_database_tools//tools/hdf5-1.8.16/hdf5/:$PATH
export PATH=/data/jh7x3/GFOLD/GFOLD_database_tools//tools/CGAL-4.8.1:$PATH
## CGAL-4.8.1 will increase foxs performance
export PATH=/data/jh7x3/GFOLD/GFOLD_database_tools//tools/fftw-3.3.4/:$PATH
## sometimes the multifit.so will failed, but it is okay to include fftw-3.3.4, won't influence other lib
export PATH=/data/jh7x3/GFOLD/GFOLD_database_tools//tools/doxygen-1.8.6/bin/:$PATH
export PATH=/data/jh7x3/GFOLD/GFOLD_database_tools//tools/gsl-2.1/:$PATH
export LD_LIBRARY_PATH=/data/jh7x3/GFOLD/GFOLD_database_tools//tools/opencv/lib:$LD_LIBRARY_PATH
mkdir -p /data/jh7x3/GFOLD/GFOLD_database_tools//tools/IMP2.6/
cd /data/jh7x3/GFOLD/GFOLD_database_tools//tools/IMP2.6/
/data/jh7x3/GFOLD/GFOLD_database_tools//tools/cmake-3.5.2/bin/cmake /data/jh7x3/GFOLD/GFOLD_database_tools//tools/imp-2.6.2/  -DCMAKE_INSTALL_PREFIX=/data/jh7x3/GFOLD/GFOLD_database_tools//tools/IMP2.6/  -DIMP_DOXYGEN_FOUND=""
make
make install
echo "installed" > /data/jh7x3/GFOLD/GFOLD_database_tools//tools/imp-2.6.2/install.done

