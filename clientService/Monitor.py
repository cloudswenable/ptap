#!/usr/bin/env python 
import time
import subprocess
import os
import ConfigParser


class MonitorConfig(object):
    def __init__(self):
        self.base_path = os.path.dirname((os.path.abspath(__file__)))
        self.root_path = os.path.dirname(self.base_path)
        self.output_file = None

    def getOutputPath(self):pass

    def toTuple(self): pass


class Monitor(object):
    def __init__(self, config=MonitorConfig()):
        self.config = config

    def run(self, rPath, pid, duration, delay_time): pass

    def runCommand(self, output_path, command, delay_time): pass

    def run(self, job): pass


