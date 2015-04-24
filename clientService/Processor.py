__author__ = 'ysun49'
import os
import ConfigParser
import sys
import subprocess
rootpath = os.path.dirname(os.path.realpath(sys.path[0]))
if not rootpath in sys.path:
        sys.path.append(rootpath)
from clusterService.ResultModel import *
from clusterService.ResultManager import *
import threading

class ProcessorConfig(object):
    def __init__(self, job_info=None):
        self.config = ConfigParser.ConfigParser()
        self.base_path = os.path.dirname(__file__)
        self.root_path = os.path.dirname(self.base_path)
        self.file_name = None
        self.job_info = job_info
        # sometimes there is no job instance(e.g. we use the commandline tool perf-hotspots.py ), the job_info will be used

    def getInputFile(self):pass

    def getOutputPath(self):pass

class Processor(threading.Thread):
    def __init__(self, config=ProcessorConfig()):
        threading.Thread.__init__(self)
        self.config = config

    def handle(self, job): pass

    def run(self):
        results = self.handle(self.job or self.config.job_info)
        for result in results:
                outfile = open(result.path, 'w')
                outfile.write(result.dumps())
                outfile.close()
                subprocess.call('sudo chmod 777 '+result.path, shell=True)

