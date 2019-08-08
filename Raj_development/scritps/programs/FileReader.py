import os
#reads all the file in a folder
def readFileName(input_path):
	fileNames = []
	# r=root, d=directories, f = files
	for root, directories , files in os.walk(input_path):
	    for file in files:
	        if '.txt' in file:
	            fileNames.append(file[0:len(file)-4])
	fileNames.sort()
	return fileNames;
	 

