import os   
import os.path
import time
import glob
import sys


if len(sys.argv) != 7:
	print("Wrong input parameters\n\n")
        exit()

fasta_dir = sys.argv[1]
native_dir = sys.argv[2]
secondary_structure_dir = sys.argv[3]
restraints_dir = sys.argv[4]
outputdir = sys.argv[5]
proc_num = int(sys.argv[6])



if not os.path.exists(outputdir):
	os.system("mkdir -p " + outputdir)


if not os.path.exists(fasta_dir):
	print("Failed to find "+fasta_dir)
	exit()

if not os.path.exists(native_dir):
        print("Failed to find "+native_dir)
        exit()

if not os.path.exists(secondary_structure_dir):
        print("Failed to find "+secondary_structure_dir)
        exit()

if not os.path.exists(restraints_dir):
        print("Failed to find "+restraints_dir)
        exit()



#reads all the file in a folder

fileNames = glob.glob(fasta_dir+"/*fasta")



shell_dir = outputdir + '/shell_files'

if not os.path.exists(shell_dir):
        os.system("mkdir -p " +  shell_dir)





for filepath in fileNames:
   filename = os.path.basename(filepath)
   targetid = filename.split('.')[0]  # T0949.fasta
   native_file = native_dir + '/' + targetid + '.pdb'
   ss_file = secondary_structure_dir + '/' + targetid + '.ss'
   restraint_file = restraints_dir + '/' + targetid + '.restraints'
   fasta_file = fasta_dir + '/' + targetid + '.fasta'
   if not os.path.isfile(native_file):
	continue
  
   if not os.path.isfile(ss_file):
        continue

   if not os.path.isfile(restraint_file):
        continue

   if not os.path.isfile(fasta_file):
        continue
   
   print("Generating shell script for "+ targetid+ "\n")
   workdir = outputdir + '/' + targetid + '_out'
   if not os.path.exists(workdir):
	os.system("mkdir -p " + workdir)
   
   run_file = shell_dir + '/' + targetid+".sh"
   os.system("touch "+ run_file + ".queued")
   f = open(run_file, "w")
   f.write("#!/bin/bash -l\n")
   f.write("#SBATCH -J  " + str(targetid)+ "\n") 
   f.write("#SBATCH -o "+ targetid +"-\%j.out\n")
   f.write("#SBATCH --partition Lewis,hpc4,hpc5\n")
   f.write("#SBATCH --nodes=1\n")
   f.write("#SBATCH --ntasks=1\n")
   f.write("#SBATCH --cpus-per-task=1\n")
   f.write("#SBATCH --mem-per-cpu=10G\n")
   f.write("#SBATCH --time 2-00:00\n")
   f.write("mv "+ run_file + ".queued" + " " + run_file + ".running"+ "\n")
   cmd = "sh /data/raj/GFOLD/bin/run_GFOLD.sh "+ targetid + " " + fasta_file + " " + ss_file + " " + restraint_file + " " + workdir
   f.write("printf \""+cmd+"\"\n")   
   f.write("sh /data/raj/GFOLD/bin/run_GFOLD.sh "+ targetid + " " + fasta_file + " " + ss_file + " " + restraint_file + " " + workdir + "\n")
   f.write("mv "+ run_file + ".running" + " " + run_file + ".done" + "\n")



starttime = time.time();
for filepath in fileNames:
	filename = os.path.basename(filepath)
        targetid = filename.split('.')[0]  # T0949.fasta
        run_file = shell_dir + '/' + targetid+".sh"
	print("Running "+ run_file+"\n")
	### check the running jobs
	while True:
		running_jobs_num = 1
		done_jobs_num = 0
		total_jobs_num = 0
		files_list = glob.glob(shell_dir+"/*")
		for item in files_list:
			if item[-3:] == '.sh':
				total_jobs_num +=1
			if item[-5:] == '.done':
				done_jobs_num +=1
			if item[-8:] == '.running':
				running_jobs_num +=1
		
		time.sleep(2)
		if running_jobs_num <= proc_num:
			break
		else:
			continue
	
	### submit jobs
	print("sh "+ run_file + " &> " + run_file + ".log"  + " &\n")
	os.system("sh "+ run_file + " &> " + run_file + ".log"  + " &") # run it in background
	print("Running("+str(running_jobs_num)+")" + " Done("+str(done_jobs_num)+")"+ " Total("+str(total_jobs_num)+") "  + "\n")
	time.sleep(1)

print(fileNames)

#### wait until all jobs are done
while True:
	running_jobs_num = 1
	done_jobs_num = 0
	total_jobs_num = 0
	files_list = glob.glob(shell_dir+"/*")
	for item in files_list:
		if item[-8:] == '.running':
			running_jobs_num +=1
	
	time.sleep(2)
	if running_jobs_num == 0:
		break
	else:
		continue

print("Execution Time: "+ str(time.time()-starttime))

#### run in parallel with 10 proteins one time
