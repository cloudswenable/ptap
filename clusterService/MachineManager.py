__author__ = 'jimmy'

import subprocess
import socket
import select

from Machine import *
from ManagerServer import *

class MachineManager(object):
    def __init__(self):
        self.machines = []
        self.install_cmd = "scp -r ../backgroundService/* root@%s:"
        self.start_cmd = 'ssh root@%s "python ./backgroundService/Agent.py"'
        self.server = ManagerServer()

    def start(self):
        self.server.start()
        self.server.dispatcher.start()
        self.server.connectionMonitor.start()

    def existAndActive(self, ip_addr):
        exist = False
        active = False
        for machine in self.machines:
            if machine.ip_addr == ip_addr:
                exist = True
                active = machine.is_active
        return exist, active

    def remoteInstallAgent(self, ip_addr):
        exist, active = self.existAndActive(ip_addr)
        if exist:
            if active:
                print "machine exist and alive now"
                pass
            else:
                print "machine exist but not start the agent"
                subprocess.call(self.start_cmd % (ip_addr), shell=True)
        else:
            subprocess.call(self.install_cmd % (ip_addr), shell=True)
            subprocess.call(self.start_cmd % (ip_addr), shell=True)


def main():
    manager = MachineManager()
    manager.start()

if __name__ == '__main__':
    main()
