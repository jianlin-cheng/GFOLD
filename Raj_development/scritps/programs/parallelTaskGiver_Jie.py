import os   
import os.path
from FileReader import readFileName 
import time
import glob

#reads all the file in a folder
path = '/home/rajroy/Documents/test/input'

fileNames = readFileName(path)
print(fileNames)
 

os.chdir("..") 
directory =  os.getcwd() + "/shells/"


if os.path.isdir(directory):
   	#os.rmdir(directory)
	print("Directory Exists at "+directory)
	#os.mkdir(directory)
   	print("Directory Generated at "+directory)
else:
	os.mkdir(directory)
  	print("Directory Generated at "+directory)

output_directory =  os.getcwd() + "/output/"
if os.path.isdir(output_directory):
   	os.rmdir(output_directory)
	print("Directory Exists at "+output_directory)
	os.mkdir(output_directory)
   	print("Directory Generated at "+output_directory)
else:
	os.mkdir(output_directory)
  	print("Directory Generated at "+output_directory)
os.chdir(output_directory)
print(os.getcwd());

for file in fileNames:
   print("Generate shell script "+ directory + '/' + file+".sh")
   run_file = directory + '/' + file+".sh"
   os.system("touch "+ run_file + ".queued")
   f = open(run_file, "w")
   f.write("#!/bin/bash -l\n")
   f.write("#SBATCH -J  " + str(file)+ "\n") 
   f.write("#SBATCH -o test-\%j.out\n")
   f.write("#SBATCH --partition Lewis,hpc4,hpc5\n")
   f.write("#SBATCH --nodes=1\n")
   f.write("#SBATCH --ntasks=1\n")
   f.write("#SBATCH --cpus-per-task=1\n")
   f.write("#SBATCH --mem-per-cpu=10G\n")
   f.write("#SBATCH --time 2-00:00\n")
   f.write("mv "+ run_file + ".queued" + " " + run_file + ".running"+ "\n")
   f.write("echo this is shell scripts for "+ str(file) + "\n")
   f.write("sleep 20\n")
   f.write("mv "+ run_file + ".running" + " " + run_file + ".done" + "\n")


def execute_script(input_file):
  print('Process: '+str(os.getpid()) +' :'+ str(input_file)  )
  os.system("sh "+ directory + '/' + input_file+".sh")


starttime = time.time();
for file in fileNames:
	run_file = directory + '/' + file+".sh"
	print("Running sh "+ directory + file+".sh\n")
	### check the running jobs
	while True:
		running_jobs_num = 1
		done_jobs_num = 0
		total_jobs_num = 0
		files_list = glob.glob(directory+"/*")
		for item in files_list:
			if item[-3:] == '.sh':
				total_jobs_num +=1
			if item[-5:] == '.done':
				done_jobs_num +=1
			if item[-8:] == '.running':
				running_jobs_num +=1
		
		time.sleep(2)
		if running_jobs_num <= 2:
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
	files_list = glob.glob(directory+"/*")
	for item in files_list:
		if item[-8:] == '.running':
			running_jobs_num +=1
	
	time.sleep(2)
	if running_jobs_num <= 2:
		break
	else:
		continue

print("Execution Time: "+ str(time.time()-starttime))

#### run in parallel with 10 proteins one time
