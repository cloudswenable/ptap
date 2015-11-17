#!/usr/bin/python
# -*- coding: utf-8 -*-

import subprocess
import os

__metaclass__ = type

class DeploymentControlerConfig:
        baseSourcePath = '/AllSource/ClientSourceCode'
        basePath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        def __init__(self):
            pass

        @staticmethod
        def getBaseSourcePath(relativeDir):
                tmp = DeploymentControlerConfig.basePath + '/' + DeploymentControlerConfig.baseSourcePath +'/'
                for item in relativeDir.split('/'):
                        if item:
                                tmp += item + '/'
                return tmp

        @staticmethod
        def getSourcePath(relativeDir):
                tmp = DeploymentControlerConfig.getBaseSourcePath(relativeDir)
                return tmp


class DeploymentControler:
    # Deployment type
    DOCKER = 0
    BINARY = 1

    def __init__(self, config):
	self.config = config
        
    @staticmethod
    def getDeploymentType(rpath):
        '''
            get the deployment type based on the files in the directory
        sourcePath = DeploymentControlerConfig.getSourcePath(rpath)
        if "Dockerfile" in os.listdir(sourcePath):
            return DeploymentControler.DOCKER
        else:
            return DeploymentControler.BINARY
        '''
	return DeploymentControler.BINARY

    def setStart(self, path, comFile): pass

    def deploy(self): pass

    def run(self, rPath):
	sourcePath = self.config.getSourcePath(rPath)
        self.setStart(sourcePath, sourcePath+'/start.txt')
        self.deploy()
        print "DeploymentControler run> popen args: ", self.com, self.path
        popen = subprocess.Popen(self.com, shell=True, cwd=self.path)
        pid = popen.pid
        return pid


def main():
    print '+++++++++++++++++++++START++++++++++++++++++++++++'
    dep = DeploymentControler()
    print dep.run()
    print '+++++++++++++++++++++END++++++++++++++++++++++++++'


if __name__ == '__main__':
    main()
