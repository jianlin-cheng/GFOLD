# CONFOLD-UNICON3D
Integration of CONFOLD and UNICON3D for Ab Initio Protein Structure Modeling

### Mocalpy Installation Steps On Lewis server

--------------------------------------------------------------------------------------

**(A) (Optional if already installed) Install the Mocapy tool on sunflower**  

***&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(a) Create tool directory to install Mocapy dependency***

```
> mkdir /storage/htc/bdm/tools/Mocapy_tools/
> cd /storage/htc/bdm/tools/Mocapy_tools/
```

***&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(b) Check the same version of gcc and gfortran. If exists, ignore installation, otherwise try install it and set the environment path***

```
>  gcc -v
>  gfortran -v 
     Lewis: gcc version 4.8.5 20150623 (Red Hat 4.8.5-16) (GCC)
```

***&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(c) Check the cmake version. If exists, ignore installation, otherwise try install it and set the environment path***

```
> cmake -version
	(cmake version 2.8.12.2)
```

***&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(d) Check the BLAS version. If exists, ignore installation, otherwise try install it and set the environment path***

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;d.1.	Download blas-3.6.0.tgz from http://www.netlib.org/blas/

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;d.2.	Expand the compressed package: tar xvfz blas.tgz

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;d.3.	Go to the package root directory

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;d.4.	Execute the following commands in the order given:
```
cd  /storage/htc/bdm/tools/Mocapy_tools
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
cd  /storage/htc/bdm/tools/Mocapy_tools/
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
cd  /storage/htc/bdm/tools/Mocapy_tools/
 wget http://sourceforge.net/projects/boost/files/boost/1.38.0/boost_1_38_0.tar.gz
 (If failed to wget, please download it manually from website)
./configure --prefix=/storage/htc/bdm/tools/Mocapy_tools/boost_1_38_0/
make install
(Check if boost_1_38_0/lib and boost_1_38_0/include is generated, if not, boost didn’t install correctly)
```
or better install Boost_1_55_0
```
cd  /storage/htc/bdm/tools/Mocapy_tools/
 tar -zxvf boost_1_55_0.tar.gz
 (If failed to wget, please download it manually from website)
./bootstrap.sh --prefix=/storage/htc/bdm/tools/Mocapy_tools/boost_1_55_0
./b2
./b2 install
(Check if boost_1_55_0/lib and boost_1_55_0/include is generated, if not, boost didn’t install correctly)
```
***Important: I found in different linux system Mocapy need different version of boost, maybe some gfortran/gcc version required when cmake in Mocapy.***

***For now, I found sunflower and sysbio server support Boost_1_38_0/Boost_1_55_0, but failed with Boost_1_59_0**


***&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(g) Check the Mocapy version. If exists, ignore installation, otherwise try install it and set the environment path***

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





