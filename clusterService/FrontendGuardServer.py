import socket
import random
import struct
import os
import sys
import threading
import json
from FrontendAgentClient import *
basePath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
webBasePath = basePath + '/webServer'
if not webBasePath in sys.path:
        sys.path.insert(0, webBasePath)
os.environ['DJANGO_SETTINGS_MODULE'] = 'webServer.settings'
from showControler.models import MachineModel

class FrontendGuardServer(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)

	def prepareServer(self):
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                portUsed = True
                port = 0
                while portUsed:
                        try:
                                portUsed = False
                                port = random.randint(1024, 65535)
                                self.sock.bind(('0.0.0.0', port))
                        except:
                                portUsed = True

                ip = socket.gethostbyname(socket.gethostname())
                return (ip, port)


	def run(self):
                self.sock.listen(1)
		while True:
                	clientSock, addr = self.sock.accept()
                	self.updateMachines(clientSock)
                	clientSock.send('done')
                self.sock.close()
	
	def updateMachines(self, cSock):
		message = json.loads(cSock.recv(1024))
		type = message[0]
		machineInfo = message[1]
		if type == 0:# add machine
			name = machineInfo['name']
			mac = machineInfo['mac']
			ip = machineInfo['ip_addr']
			fileno = machineInfo['fileno']
			try:
				machine = MachineModel.objects.filter(ip=ip)[0]
			except:
				machine = None
			if machine:
				machine.active = True
                                machine.fileno = machineInfo['fileno']
				machine.save()
			else:
				os_info = machineInfo['os_info']
				cpu_info = machineInfo['cpu_info']
				mem_info = machineInfo['mem_info']
				disk_info = machineInfo['disk_info']
				ht = machineInfo['ht']
				turbo = machineInfo['turbo']
				machine = MachineModel(name=name, active=True, mac=mac, ip=ip, fileno=fileno, os_info=os_info, cpu_info=cpu_info, mem_info=mem_info, disk_info=disk_info, ht=ht, turbo=turbo)
				machine.save()
		elif type == 1: # set machine active to False
			ip = machineInfo['ip_addr']
			try:
				machine = MachineModel.objects.filter(ip=ip)[0]
			except:
				machine = None
			if machine:
				machine.active = False
				machine.save()

class MachinesInfoSender:
        def __init__(self, serverIp, serverPort):
                self.serverIp = serverIp
                self.serverPort = int(serverPort)
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	def sendMachines(self, message):
		self.sock.connect((self.serverIp, self.serverPort))
		msg = message
		self.sock.send(msg)
		response = self.sock.recv(4)
		self.sock.close()

def main():
        choice = sys.argv[1]
        if choice == 'server':
                rec = FrontendGuardServer()
                ip, port = rec.prepareServer()
                print 'start server ip = ', ip , '  port = ', port
                rec.start()
		frontendAgentClient = FrontendAgentSender()
		frontendAgentClient.registerMachinesListener([ip, port])
                print 'server finished'
        elif choice == 'client':
                sen = MachinesInfoSender(sys.argv[2], int(sys.argv[3]))
                sen.sendMachines([])


if __name__ == '__main__':
        main()

