#!/usr/bin/env python
import subprocess
import sys


curr_path = sys.path[0]
paths = curr_path.split('/')[:-1]
abs_path = '/'.join(paths)

print '++++++++++++++++++++++++++++++START BACKGROUND CLIENT ++++++++++++++++++++'
print "starting clusterService/AgentClient.py ..."
subprocess.Popen(['python', abs_path + '/clusterService/AgentClient.py'])

