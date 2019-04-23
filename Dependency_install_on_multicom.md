
### IMP Installation Steps On multicom server

--------------------------------------------------------------------------------------

**(A) (Optional if already installed) Install the IMP and dependency tools on multicom**  

***&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(a) Create tool directory to install Mocapy dependency***

```
> mkdir /data/commons/tools/IMP_tools/
> cd /data/commons/tools/IMP_tools/
```

***&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(b) Check the same version of gcc and gfortran. If exists, ignore installation, otherwise try install it and set the environment path***

```
>  gcc -v
>  gfortran -v 
     multicom: gcc version 4.8.5 20150623 (Red Hat 4.8.5-36) (GCC)
```

***&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(c) Check the cmake version. If exists, ignore installation, otherwise try install it and set the environment path***

```
> cmake -version
	(cmake version 2.8.12.2)
	
```
Install cmake

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;c.1.	Download the Unix/Linux source file in tar.gz format from http://www.cmake.org/download (e.g., cmake-2.8.3.tar.gz or later)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;c.2.	Expand the compressed package: tar xvfz cmake-2.8.3.tar.gz

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;c.3.	Go to the package root directory

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;c.4.	Execute the following commands in the order given:

```
	cd  /data/commons/tools
	wget https://cmake.org/files/v2.8/cmake-2.8.12.2.tar.gz
	Download and uncompress tar –zxvf cmake-2.8.12.2.tar.gz
	cd cmake-2.8.12.2
	./bootstrap --prefix=/data/commons/tools/cmake-2.8.12.2
	gmake
	make install (require administrative) or try 
	make DESTDIR=/data/commons/tools/cmake-2.8.12.2/ install
	alias cmake=/data/commons/tools/cmake-2.8.12.2/bin/cmake
	cmake
	cmake --version
```
and cmake3.5.2

```
	cd  /data/commons/tools
	wget https://cmake.org/files/v3.5/cmake-3.5.2.tar.gz
	Download and uncompress tar –zxvf cmake-3.5.2.tar.gz
	cd cmake-3.5.2
	./bootstrap --prefix=/data/commons/tools/cmake-3.5.2
	gmake
	make install (require administrative) or try 
	make DESTDIR=/data/commons/tools/cmake-3.5.2/ install
	alias cmake=/data/commons/tools/cmake-3.5.2/bin/cmake
	cmake
	cmake --version
```


***&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(d) Check the BLAS version. If exists, ignore installation, otherwise try install it and set the environment path***

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;d.1.	Download blas-3.6.0.tgz from http://www.netlib.org/blas/

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;d.2.	Expand the compressed package: tar xvfz blas.tgz

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;d.3.	Go to the package root directory

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;d.4.	Execute the following commands in the order given:
```
	cd  /data/commons/tools/IMP_tools/
	wget http://www.netlib.org/blas/blas-3.6.0.tgz(If failed to wget, please download it manually from website)
	tar -zxvf blas-3.6.0.tgz 
	cd BLAS-3.6.0/
	make
	mv blas_LINUX.a libblas.a
	sudo cp libblas.a /usr/local/lib/(if don’t have permission, can use lib directory when compile mocapy)
```

***&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(e) Check the LAPACK version. If exists, ignore installation, otherwise try install it and set the environment path***

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;e.1.	Download lapack-3.4.1.tgz from http://www.netlib.org/lapack/Expand the compressed package: tar xvfz lapack-3.4.1.tgz

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;e.2.	Go to the package root directory

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;e.3.	Execute the following commands in the order given:

```
	cd  /data/commons/tools/IMP_tools/
	wget http://www.netlib.org/lapack/lapack-3.4.1.tgz(If failed to wget, please download it manually from website)
	tar -zxvf lapack-3.4.1.tgz
	cd lapack-3.4.1
	cp make.inc.example make.inc
	make blaslib  # To generate the Reference BLAS Library
	make
	sudo cp liblapack.a /usr/local/lib/(if don’t have permission, can use lib directory when compile mocapy)
```

***&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(f) Check the BOOST version. If exists, ignore installation, otherwise try install it and set the environment path***

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;f.1.	Download the the .tar.gz from http://www.boost.org/users/history/version_1_38_0.html

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;f.2.	Expand the compressed package: boost_1_38_0.tar.gz

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;f.3.	Go to the package root directory

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;f.4.	Execute the following commands in the order given:

```
	cd  /data/commons/tools/
	 wget http://sourceforge.net/projects/boost/files/boost/1.38.0/boost_1_38_0.tar.gz
	 (If failed to wget, please download it manually from website)
	./configure --prefix=/data/commons/tools/boost_1_38_0/
	make install
	(Check if boost_1_38_0/lib and boost_1_38_0/include is generated, if not, boost didn’t install correctly)
```
or better install Boost_1_55_0
```
	cd  /data/commons/tools/
	 tar -zxvf boost_1_55_0.tar.gz
	 (If failed to wget, please download it manually from website)
	 cd boost_1_55_0
	./bootstrap.sh --prefix=/data/commons/tools/boost_1_55_0
	./b2
	./b2 install
	(Check if boost_1_55_0/lib and boost_1_55_0/include is generated, if not, boost didn’t install correctly)
```
***Important: I found in different linux system Mocapy need different version of boost, maybe some gfortran/gcc version required when cmake in Mocapy.***

***For now, I found sunflower and sysbio server support Boost_1_38_0/Boost_1_55_0, but failed with Boost_1_59_0**



***&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(g) Install install hdf5 with zlib. Check the dependecies of IMP in http://www.integrativemodeling.org/2.6.1/doc/manual/installation.html***

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;g.1.	install hdf5 with zlib

```
	cd /data/commons/tools/IMP_tools

	tar -zxvf zlib-1.2.8.tar.gz
	cd zlib-1.2.8
	./configure  --prefix=/data/commons/tools/IMP_tools/zlib-1.2.8
	make
	make install


	tar -zxvf hdf5-1.8.16.tar.gz
	cd hdf5-1.8.16
	./configure --with-zlib=/data/commons/tools/IMP_tools/zlib-1.2.8/
	make 
	make install
```


***&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(h) Install install GSL  http://www.linuxfromscratch.org/blfs/view/svn/general/gsl.html, ftp://ftp.gnu.org/pub/gnu/gsl/gsl-2.1.tar.gz***

```
	cd /data/commons/tools/IMP_tools
	wget ftp://ftp.gnu.org/pub/gnu/gsl/gsl-2.1.tar.gz
	tar -zxvf gsl-2.1.tar.gz
	cd gsl-2.1
	./configure  --prefix=/data/commons/tools/IMP_tools/gsl-2.1/
	make
	make install
```

***&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(i) install gmp ***
```
	 cd /data/commons/tools/IMP_tools/gmp-4.3.2
	 ./configure --prefix=/data/commons/tools/IMP_tools/gmp-4.3.2
	 make 
	 make install
```
or install gmp as static library in future when building static tool

```
	 cd /data/commons/tools/IMP_tools/gmp-4.3.2
	 ./configure --prefix=/data/commons/tools/IMP_tools/gmp-4.3.2  --enable-static --disable-shared
	 make 
	 make install
```


***&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(j) build mpft***
```
	cd /data/commons/tools/IMP_tools/mpfr-2.4.2/
	./configure --prefix=/data/commons/tools/IMP_tools/mpfr-2.4.2/ --with-gmp-build=/data/commons/tools/IMP_tools/gmp-4.3.2
	make
	make install
```

or install mpft as static library in future when building static tool

```
	cd /data/commons/tools/IMP_tools/mpfr-2.4.2/
	./configure --prefix=/data/commons/tools/IMP_tools/mpfr-2.4.2/ --enable-static --disable-shared  --with-gmp-build=/data/commons/tools/IMP_tools/gmp-4.3.2
	make
	make install
```

***&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(i) Install install CGAL from https://github.com/CGAL/cgal/releases, http://doc.cgal.org/latest/Manual/installation.html***

```
	cd /data/commons/tools/IMP_tools
	wget https://github.com/CGAL/cgal/releases/download/releases%2FCGAL-4.8.1/CGAL-4.8.1.tar.xz 
	tar -xvf CGAL-4.8.1.tar.xz
	cd CGAL-4.8.1
	export PATH=/data/commons/tools/IMP_tools/gmp-4.3.2/:$PATH
	export PATH=/data/commons/tools/IMP_tools/mpfr-2.4.2/:$PATH
	export BOOST_ROOT="/data/commons/tools/boost_1_55_0"
	export BOOST_INCLUDE="/data/commons/tools/boost_1_55_0/include"
	export BOOST_LIBDIR="/data/commons/tools/boost_1_55_0/lib"
	export BOOST_OPTS="-DBOOST_ROOT=${BOOST_ROOT} -DBOOST_INCLUDEDIR=${BOOST_INCLUDE} -DBOOST_LIBRARYDIR=${BOOST_LIBDIR}"
	cmake .   (cmake require >2.8.10)
	make

	export PATH=/data/commons/tools/IMP_tools/CGAL-4.8.1:$PATH

```

or install cgal as static library in future when building static tool

```
	add to cgal-releases-CGAL-4.8.1/CMakeLists.txt 
			set(BUILD_SHARED_LIBS false)
			export PATH=/data/commons/tools/IMP_tools/gmp-4.3.2/:$PATH
			export PATH=/data/commons/tools/IMP_tools/mpfr-2.4.2/:$PATH
			/data/commons/tools/cmake-2.8.12.2/bin/cmake -DCMAKE_BUILD_TYPE=Debug  ./ -DBUILD_SHARED_LIBS=false
			make
```


***&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(j) Install FFTW http://www.fftw.org/download.html***

```
	cd /data/commons/tools/IMP_tools
	wget ftp://ftp.fftw.org/pub/fftw/fftw-3.3.4.tar.gz
	tar -zxvf fftw-3.3.4.tar.gz
	 ./configure --prefix=/data/commons/tools/IMP_tools/fftw-3.3.4 --enable-shared  --with-pic
	 make 
	 make install
```

***&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(j) Install libTau***

```
	cd /data/commons/tools/IMP_tools
	wget https://integrativemodeling.org/libTAU/libTAU-1.0.1.zip
	unzip libTAU-1.0.1.zip
	export CFLAGS="$CFLAGS -I/data/commons/tools/IMP_tools/libTAU-1.0.1/include"
	export LDFLAGS="$LDFLAGS -L/data/commons/tools/IMP_tools/libTAU-1.0.1//lib" 
```

***&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(k) Install openCV  http://docs.opencv.org/3.0-beta/doc/tutorials/introduction/linux_install/linux_install.html***
```
	cd /data/commons/tools/IMP_tools
	git clone https://github.com/Itseez/opencv.git
	cd opencv
	mkdir release
	/data/commons/tools/cmake-3.5.2/bin/cmake -D CMAKE_BUILD_TYPE=RELEASE -D  CMAKE_INSTALL_PREFIX=/data/commons/tools/IMP_tools/opencv/release ..
	make -j 8
	make install
```
	

	



***&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(l) Install doxygen  http://www.stack.nl/~dimitri/doxygen/download.html, https://geeksww.com/tutorials/miscellaneous/bison_gnu_parser_generator/installation/installing_bison_gnu_parser_generator_ubuntu_linux.php ***
```
	 wget http://ftp.gnu.org/gnu/bison/bison-2.3.tar.gz
	 cd bison-2.3/

	git clone https://github.com/doxygen/doxygen.git
	cd doxygen

	mkdir build
	cd build
	cmake -G "Unix Makefiles" ..
	make

	tar -zxvf doxygen-1.8.6.linux.bin.tar.gz
	cd doxygen-1.8.6
```
	


### download imp-2.6.2.tar.gz from  https://integrativemodeling.org
cd /storage/htc/bdm/tools/Mocapy_tools/
tar -zxvf imp-2.6.2.tar.gz
mkdir IMP2.6















**(B) (Optional if already installed) Install the IMP tools on multicom for c++ developement, which is Dynamic Bayesian Network toolkit** 

***&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(a) Check the Mocapy version. If exists, ignore installation, otherwise try install it and set the environment path***

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;g.1.	Download Mocapy++-1.07.tar.gz from https://sourceforge.net/projects/mocapy/

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;g.2.	Expand the compressed package: tar xvfz Mocapy++-1.07.tar.gz

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;g.3.	Go to the package root directory

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;g.4.	Before compilation, we should manually change some setting in the CMakeLists.txt, and examples/CMakeLists.txt


```
## For Linux
cd /storage/htc/bdm/tools/Mocapy_tools/Mocapy++-1.07
edit ./CMakeLists.txt, and comment #add_subdirectory (tests), we don’t need this
edit ./examples/CMakeLists.txt, and
1.	add: SET(BLAS_LIBRARY "/storage/htc/bdm/tools/Mocapy_tools/BLAS-3.6.0/libblas.a")
2.	change part of code by adding ${BLAS_LIBRARY} (Be careful of the space between variables)
       FOREACH(p ${PROGS})
        add_executable(${p} ${p}.cpp)
        target_link_libraries (${p} ${MOCAPYLIB} ${Boost_SERIALIZATION_LIBRARY} ${LAPACK_LIBRARY} ${BLAS_LIBRARY} ${CMAKE_FLIB})
ENDFOREACH(p)
```
       
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;g.5.	Execute the following commands in the order given:

#Lewis: 
```
cd /storage/htc/bdm/tools/Mocapy_tools/Mocapy++-1.07
export LD_LIBRARY_PATH=/storage/htc/bdm/tools/Mocapy_tools/boost_1_55_0/lib:$LD_LIBRARY_PATH
cmake -DBOOST_ROOT='/storage/htc/bdm/tools/Mocapy_tools/boost_1_55_0/' -DLAPACK_LIBRARY:FILEPATH='/storage/htc/bdm/tools/Mocapy_tools/lapack-3.4.1/liblapack.a' .
make
cd examples
./hmm_simple
```





