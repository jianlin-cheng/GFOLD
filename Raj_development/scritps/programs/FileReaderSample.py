
import os
import sys
import re



test_script_dir = '/home/rajroy/Documents/test/input'

if not os.path.isdir(test_script_dir):
    print(test_script_dir, " does not exist.")
    sys.exit(1)


input_files = []
for r, d, f in os.walk(test_script_dir):
    for file in f:
        if file.find('.txt') == len(file) - 3:
            input_files.append(os.path.join(r, file))

input_files.sort()
print(input_files);