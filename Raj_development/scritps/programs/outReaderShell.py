pipe = Popen("pwd", shell=True, stdout=PIPE).stdout
output = pipe.read()