#!/bin/bash
#SBATCH -J  GFOLD
#SBATCH -o GFOLD-%j.out
#SBATCH --partition Lewis,hpc5,hpc4
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=10G
#SBATCH --time 1-00:00


mkdir -p /data/raj/GFOLD/test_out/1AYO-B/
cd /data/raj/GFOLD/test_out/1AYO-B/




export LD_LIBRARY_PATH=/data/raj/GFOLD/tools/modeller-9.16/lib/x86_64-intel8/:/data/raj/GFOLD/tools/IMP2.6/lib:/data/raj/GFOLD/tools/boost_1_55_0/lib:$LD_LIBRARY_PATH
PYTHONPATH="/data/raj/GFOLD/tools/IMP2.6/lib:/data/raj/GFOLD/tools/modeller-9.16/lib/x86_64-intel8/python2.5/:/data/raj/GFOLD/tools/modeller-9.16/modlib/:$PYTHONPATH"
export PYTHONPATH



if [[ ! -f "/data/raj/GFOLD/test_out/1AYO-B/1AYO-B/1AYO-B_GFOLD.pdb" ]];then 
	printf "python /data/raj/GFOLD/src/GFOLD.py  --target 1AYO-B  --fasta /data/raj/GFOLD/examples/1AYO-B.fasta --ss /data/raj/GFOLD/examples/1AYO-B.ss  --hbond 1 --restraints /data/raj/GFOLD/examples/1AYO-B.restraints --type CB --distdev 0.1  --epoch 10  --cgstep 100  --dir  /data/raj/GFOLD/test_out/1AYO-B/ --sep 1\n\n"
	python /data/raj/GFOLD/src/GFOLD.py  --target 1AYO-B  --fasta /data/raj/GFOLD/examples/1AYO-B.fasta --ss /data/raj/GFOLD/examples/1AYO-B.ss  --hbond 1 --restraints /data/raj/GFOLD/examples/1AYO-B.restraints --type CB --distdev 0.1  --epoch 10  --cgstep 100  --dir  /data/raj/GFOLD/test_out/1AYO-B/ --sep 1 
fi

printf "\nFinished.."
printf "\nCheck log file </data/raj/GFOLD/test_out/1AYO-B.log>\n\n"


if [[ ! -f "/data/raj/GFOLD/test_out/1AYO-B/1AYO-B/1AYO-B_GFOLD.pdb" ]];then 
	printf "!!!!! Failed to run GFOLD, check the installation </data/raj/GFOLD/src/>\n\n"
else
	printf "\nJob successfully completed!"
	printf "\nResults: /data/raj/GFOLD/test_out/1AYO-B/1AYO-B/1AYO-B_GFOLD.pdb\n\n"
fi

printf "Validating the results\n\n";
printf "/data/raj/GFOLD/tools/TMscore  /data/raj/GFOLD/test_out/1AYO-B/1AYO-B/1AYO-B_GFOLD.pdb  /data/raj/GFOLD/installation/benchmark/native_structure/1AYO-B.pdb\n\n"
/data/raj/GFOLD/tools/TMscore  /data/raj/GFOLD/test_out/1AYO-B/1AYO-B/1AYO-B_GFOLD.pdb  /data/raj/GFOLD/installation/benchmark/native_structure/1AYO-B.pdb

