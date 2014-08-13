#!/usr/bin/env python
import os
import sys
import re
import subprocess
from PythonTidy import tidy_up

ROOT_DIR = os.path.dirname((sys.argv[0]))
FILTERS = ['webServer', 'backgroundService']

def formatCode(path):
    list_dirs = os.listdir(path)
    for dir in list_dirs:
        new_path = os.path.join(path, dir)
        if os.path.isdir(new_path):
            formatCode(new_path)
        if os.path.isfile(new_path):
            re_object = re.compile("\w*py$")
            if re_object.search(new_path):
                new_path_back = new_path + ".bak"
                tidy_up(new_path, new_path_back)
                cmd = "mv " + new_path_back + " " + new_path
                print cmd
                subprocess.call(cmd, shell=True)

def main():
    list_dirs = os.listdir(ROOT_DIR)
    for dir in list_dirs:
        if dir in FILTERS:
            path = os.path.join(ROOT_DIR, dir)
            formatCode(path)


if __name__ == '__main__':
    main()
