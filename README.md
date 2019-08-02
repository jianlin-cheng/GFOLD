# The GFOLD protein structure system using gradient descent and residue-residue distance. 


**(1) Download GFOLD package (short path is recommended)**

```
git clone https://github.com/jianlin-cheng/GFOLD.git

(If fail, try username) git clone https://huge200890@github.com/jianlin-cheng/GFOLD.git

cd GFOLD
```

**(2) Setup the tools and download the database (required)**

```
perl setup_database.pl
```

**(3) Configure GFOLD system (required)**

```
a. edit configure.pl

b. set the path of variable '$GFOLD_db_tools_dir' for multicom databases and tools (i.e., /data/commons/GFOLD_db_tools).

c. save configure.pl

perl configure.pl
```

**(4) Testing the GFOLD method (recommended)**


```

cd examples

sh T0_run_GFOLD-1ALY-A.sh

sh T0_run_GFOLD-1AYO-B.sh

sh T0_run_GFOLD-1BYR-A.sh

sh T0_run_GFOLD-1CCW-C.sh

sh T0_run_GFOLD-1G5T-A.sh
```



**(5) Run GFOLD for structure folding**

```
   Usage:
   $ sh bin/run_GFOLD.sh <target id> <file name>.fasta <path of predicted secondary structure> <path of restraints> <output folder>

   Example:
   $ sh bin/run_GFOLD.sh 1ALY-A  /data/jh7x3/GFOLD/examples/1ALY-A.fasta  /data/jh7x3/GFOLD/examples/1ALY-A.ss  /data/jh7x3/GFOLD/examples/1ALY-A.restraints  /data/jh7x3/GFOLD/test_out/1ALY-A_out
   
  
