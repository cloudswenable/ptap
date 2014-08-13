#!/usr/bin/python
# -*- coding: utf-8 -*-

import subprocess
import os

__metaclass__ = type

class DeploymentControlerConfig:
        def __init__(self):
		self.basePath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
		self.baseSourcePath = '/AllSource/ClientSourceCode'

        def getBaseSourcePath(self, relativeDir):
                tmp = self.basePath + '/' + self.baseSourcePath +'/'
                for item in relativeDir.split('/'):
                        if item:
                                tmp += item + '/'
                return tmp

        def getSourcePath(self, relativeDir):
                tmp = self.getBaseSourcePath(relativeDir)
                return tmp


class DeploymentControler:

    def __init__(self, config):
	self.config = config

    def setStart(self, path, comFile): pass

    def deploy(self): pass

    def run(self, rPath):
	sourcePath = self.config.getSourcePath(rPath)
        self.setStart(sourcePath, sourcePath+'/start.txt')
        self.deploy()
        popen = subprocess.Popen(self.com, shell=True, cwd=self.path)
        pid = popen.pid
        return pid

class SourceDeploymentControler(DeploymentControler):

    def __init__(self, config=DeploymentControlerConfig()):
	super(SourceDeploymentControler, self).__init__(config)
	

    def setStart(self, path='../sourceCodes',
                 comFile='../sourceCodes/start.txt'):
        self.path = path
        self.com = open(comFile).readline().strip()


def main():
    print '+++++++++++++++++++++START++++++++++++++++++++++++'
    dep = DeploymentControler()
    print dep.run()
    print '+++++++++++++++++++++END++++++++++++++++++++++++++'


if __name__ == '__main__':
    main()
