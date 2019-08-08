#!/bin/sh
# DeepRank prediction file for protein quality assessment #
if [ $# -lt 5 ]
then
	echo "need four parameters : target id, path of fasta sequence, path of predicted secondary structure, path of restraints, directory of output"
	exit 1
fi

targetid=$1 
fasta=$2 
secondary_structure=$3 
restraints=$4 
outputfolder=$5 

if [ $# -eq 5 ]
then
	contact_file=$5
	nativefile='None'
fi

if [ $# -eq 6 ]
then
	contact_file=$5
	nativefile=$6
fi


if [[ "$fasta" != /* ]]
then
   echo "Please provide absolute path for $fasta"
   exit
fi

if [[ "$outputfolder" != /* ]]
then
   echo "Please provide absolute path for $outputdir"
   exit
fi


mkdir -p $outputfolder
cd $outputfolder



export LD_LIBRARY_PATH=/data/raj/GFOLD/tools/modeller-9.16/lib/x86_64-intel8/:/data/raj/GFOLD/tools/IMP2.6/lib:/data/raj/GFOLD/tools/boost_1_55_0/lib:$LD_LIBRARY_PATH
PYTHONPATH="/data/raj/GFOLD/tools/IMP2.6/lib:/data/raj/GFOLD/tools/modeller-9.16/lib/x86_64-intel8/python2.5/:/data/raj/GFOLD/tools/modeller-9.16/modlib/:$PYTHONPATH"
export PYTHONPATH

printf "python /data/raj/GFOLD/src/GFOLD.py  --target $targetid  --fasta $fasta --ss $secondary_structure  --hbond 1 --restraints $restraints --type CB --distdev 0.1  --epoch 10  --cgstep 100  --dir  $outputfolder --sep 1\n\n"
python /data/raj/GFOLD/src/GFOLD.py  --target $targetid  --fasta $fasta --ss $secondary_structure  --hbond 1 --restraints $restraints --type CB --distdev 0.1  --epoch 10  --cgstep 100  --dir  $outputfolder --sep 1



