#!/usr/bin/env python
import time
import subprocess
import os

basePath = os.path.dirname(os.path.abspath(__file__))

subprocess.Popen(['python', basePath + '/startServer.py'])
time.sleep(3)
subprocess.Popen(['python', basePath + '/startFrontend.py'])
time.sleep(3)
subprocess.Popen(['python', basePath + '/startClient.py'])
