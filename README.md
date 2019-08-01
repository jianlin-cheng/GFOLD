# The GFOLD protein structure system using gradient descent and residue-residue distance. 


**(1) Download GFOLD package (short path is recommended)**

```
git clone https://github.com/jianlin-cheng/GFOLD.git
cd GFOLD
```

**(2) Setup the tools and download the database (required)**

```
perl setup_database.pl
```

**(3) Configure GFOLD system (required)**

```
a. edit configure.pl

b. set the path of variable '$GFOLD_db_tools_dir' for multicom databases and tools (i.e., /home/GFOLD_db_tools/).

c. save configure.pl

perl configure.pl
```
