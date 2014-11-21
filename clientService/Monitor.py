#!/usr/bin/env python 
import time
import subprocess
import os
import ConfigParser
import threading

class MonitorConfig(object):
    def __init__(self):
        self.base_path = os.path.dirname((os.path.abspath(__file__)))
        self.root_path = os.path.dirname(self.base_path)
        self.output_file = None

    def getOutputPath(self):pass

    def toTuple(self): pass


class Monitor(threading.Thread):
    def __init__(self, config=MonitorConfig()):
        threading.Thread.__init__(self)
        self.config = config
        self.job = None
        self.running = True

#    def run(self, rPath, pid, duration, delay_time): pass

    def runCommand(self, output_path, command, delay_time): pass

    def run(self): pass

    def monitor(self, args): pass


