#!/usr/bin/python
# -*- coding: utf-8 -*-

import subprocess
import os
import sys
import re
from Deployment import DeploymentControler, DeploymentControlerConfig
from docker import Client


class DockerDeploymentControler(DeploymentControler):

    def __init__(self, rpath):
        super(DockerDeploymentControler, self).__init__(DeploymentControlerConfig())
        self.rpath = rpath
        self.sourcePath = self.config.getSourcePath(rpath)
        self._cli = None

    @property
    def cli(self):
        if self._cli is None:
            self._cli = Client(base_url='unix://var/run/docker.sock', version="auto")
        return self._cli

    def clean_to_valid_tag(self, st):
        return re.sub(r'[^a-z0-9-_.]', '-', st)

    def get_image_id_from_response(self, response):
        ids = re.findall(r"Successfully built (.{12})", response[-1])
        if len(ids) > 0:
            return ids[0]
        return None

    def build_image(self):
        cli = self.cli
        response = [line for line in cli.build(
            path=self.sourcePath, rm=True, tag=self.clean_to_valid_tag(self.rpath)
        )]
        return self.get_image_id_from_response(response)
    
    def start(self, image_id):
        cli = self.cli
        container = cli.create_container(image=image_id)
        response = cli.start(container=container.get('Id'))
        return container.get('Id')

    def stop(self, container_id):
        print self.cli.stop(container_id)

    def get_pids(self, container_id):
        top_info = self.cli.top(container_id)
        index = top_info["Titles"].index("PID")
        return [int(p[index]) for p in top_info["Processes"]]
        


def main():
    print '+++++++++++++++++++++START++++++++++++++++++++++++'
    dockerControler = DockerDeploymentControler(sys.argv[1]) # sys.argv[1] may be sth like "projectname/binaryname/source/1.0"
    image_id = dockerControler.build_image()
    container_id = dockerControler.start(image_id)
    print container_id, "started"
    print dockerControler.get_pids(container_id)
    import time
    time.sleep(10)
    dockerControler.stop(container_id)
    print '+++++++++++++++++++++END++++++++++++++++++++++++++'


if __name__ == '__main__':
    #main()
    DeploymentControlerConfig.getDeploymentType(sys.argv[1])
