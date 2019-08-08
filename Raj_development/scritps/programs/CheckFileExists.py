import os.path

os.chdir("..") 
directory =  os.getcwd() + "/shells/"
print(directory)

if os.path.isdir(directory):
    print "This File Exists"
else:
    print "This File Doesnt Exists"