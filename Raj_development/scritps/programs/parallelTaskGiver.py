import os   
import os.path
from FileReader import readFileName 
import time
import multiprocessing
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
   f = open(directory + '/' + file+".sh", "w")
   f.write("#!/bin/bash -l\n")
   f.write("#SBATCH -J  " + str(file)+ "\n") 
   f.write("#SBATCH -o test-\%j.out\n")
   f.write("#SBATCH --partition Lewis,hpc4,hpc5\n")
   f.write("#SBATCH --nodes=1\n")
   f.write("#SBATCH --ntasks=1\n")
   f.write("#SBATCH --cpus-per-task=1\n")
   f.write("#SBATCH --mem-per-cpu=10G\n")
   f.write("#SBATCH --time 2-00:00\n")
   f.write("echo this is shell scripts for "+ str(file) +   " &\n")
   f.write("sleep 5\n")


def execute_script(input_file):
  print('Process: '+str(os.getpid()) +' :'+ str(input_file)  )
  os.system("sh "+ directory + '/' + input_file+".sh")

pool = multiprocessing.Pool(processes=3)
starttime = time.time();
for file in fileNames:
	print("Running sh "+ directory + file+".sh\n")
	pool.map(execute_script,file)
print("Execution Time: "+ str(time.time()-starttime))

	#### run in parallel with 10 proteins one time
