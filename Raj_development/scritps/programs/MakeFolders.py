import os

# define the name of the directory to be created
print (os.getcwd())
#current directory
#mycwd = os.getcwd()
#go to previous directory
#os.chdir("..")
print(os.chdir(".."))
print (os.getcwd())
#do stuff in parent directory
path =  os.getcwd() + "/shells"
print(path)
# define the access rights
#access_rights = 0o755

try:
    os.mkdir(path)
except OSError:
   print ("Creation of the directory %s failed" % path)
else:
   print ("Successfully created the directory %s" % path)