#!/usr/bin/env python 
import subprocess
import sys
import re

curr_path = sys.path[0]
print '++++++++++++++++++++++++++STOP ALL++++++++++++++++++++++++++'
c = subprocess.Popen('ps auxww | grep python', shell=True, stdout=subprocess.PIPE)
s = c.communicate()
commands = s[0].split('\n')
pa = re.compile('\\d{1,6}')
for command in commands:
    if command.find('ptap')>=0:
	gs = pa.search(command)
	pid = gs.group(0)
	print 'kill : ', pid 
	subprocess.call(['kill', pid])
