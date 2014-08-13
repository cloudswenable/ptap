#!/usr/bin/env python
import subprocess
import sys
import time


curr_path = sys.path[0]
paths = curr_path.split('/')[:-1]
abs_path = '/'.join(paths)

print "++++++++++++++++++++START FRONTEND +++++++++++++++++++++++"
print "starting webServer/server..."
subprocess.Popen(['python', abs_path + '/webServer/manage.py', 'runserver', 'localhost:8000'])

print "starting clusterService/FrontendGuardServer ..."
subprocess.Popen(['python', abs_path + '/clusterService/FrontendGuardServer.py', 'server'])
