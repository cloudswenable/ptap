#!/usr/bin/python
# -*- coding: utf-8 -*-

import subprocess
import os
import sys
from Deployment import DeploymentControler, DeploymentControlerConfig


class SourceDeploymentControler(DeploymentControler):

    def __init__(self, config=DeploymentControlerConfig()):
	super(SourceDeploymentControler, self).__init__(config)
	

    def setStart(self, path='../sourceCodes',
                 comFile='../sourceCodes/start.txt'):
        self.path = path
        self.com = open(comFile).readline().strip()


def main():
    print '+++++++++++++++++++++START++++++++++++++++++++++++'
    sourceCodeControler = SourceDeploymentControler()
    pid = sourceCodeControler.run(sys.argv[1])
    print pid
    print '+++++++++++++++++++++END++++++++++++++++++++++++++'


if __name__ == '__main__':
    main()
