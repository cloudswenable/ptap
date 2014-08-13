#!/usr/bin/env python
import subprocess
import sys
import time


curr_path = sys.path[0]
paths = curr_path.split('/')[:-1]
abs_path = '/'.join(paths)

print "++++++++++++++++++++START SERVER+++++++++++++++++++++++"

print "starting clusterService/MachineManager.py ..."
subprocess.Popen(['python', abs_path + '/clusterService/MachineManager.py'])
time.sleep(1)

