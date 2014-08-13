__author__ = 'jimmy'

import select
import socket
import threading
from ClusterConfig import *
from ClientConnection import *
from MessageReceiver import *
from MessageSender import *
from Dispatcher import *
from FrontendGuardServer import *
import Queue
import time
import traceback
from ConnectionMonitor import *

class ManagerServer(threading.Thread):
    serverName = 'ManagerServer'
    def __init__(self, config=ServerConfig()):
        threading.Thread.__init__(self)
        self.config = config
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_addr = (self.config.bind_addr, self.config.bind_port)
        self.socket.bind(server_addr)
        self.queue = Queue.Queue()
        self.dispatcher = Dispatcher(self.queue)
        self.epoll = select.epoll()
        self.connections = {}
	self.machines = {}
	self.listeners = []
        self.clientConnections = []
        self.connectionMonitor = ConnectionMonitor(self.config.interval, self, self.clientConnections)

    def switchToClient(self, fileno, message):
	tmpConnection = self.connections.get(int(fileno))
	if tmpConnection:
		tmpConnection.enqueue(message)

    def isCenterServer(self):
	return True

    def enqueue(self, data):
        if data:
            self.queue.put(data)

    def register(self, ip, port):
	self.listeners.append((ip, port))

    def notifyAllListeners(self, message):
	# 0: add machine , 1: delete machine
	for ip, port in self.listeners:
		try:
			sender = MachinesInfoSender(ip, int(port))
			sender.sendMachines(json.dumps(message))
		except: pass
	
    def addMachine(self, machine):
	fileno = str(machine.fileno)
	self.machines[fileno] = machine
	machineInfo = {'name':machine.name, 'mac':machine.mac, 'ip_addr':machine.ip_addr, 'fileno': machine.fileno, 'os_info':machine.os_info, 'cpu_info':machine.cpu_info, 'mem_info':machine.mem_info, 'disk_info':machine.disk_info, 'ht':machine.ht, 'turbo':machine.turbo}
	self.notifyAllListeners([0, machineInfo])
		
    def removeMachine(self, fileno):
        fileno = str(fileno)
	if self.machines.has_key(fileno):
		machine = self.machines[fileno]
		machineInfo = {'ip_addr':machine.ip_addr}
		self.notifyAllListeners([1, machineInfo])
	        del self.machines[fileno]

    def removeConnection(self, sock):
	fileno = sock.fileno()
	if self.connections.has_key(fileno):
		self.removeMachine(fileno)
		tmpConnection = self.connections[fileno]
                try:
                        if tmpConnection in self.clientConnections:
                                del self.clientConnections[self.clientConnections.index(tmpConnection)]
                except:
                        traceback.print_exc()
		self.epoll.unregister(tmpConnection.sock.fileno())
		tmpConnection.close()
		del self.connections[fileno]

    def addClientConnection(self, connection):
        if not connection in self.clientConnections:
                self.clientConnections.append(connection)

    def addConnection(self, sock, ip_addr):
        fileno = sock.fileno()
        conn = ClientConnection(self, sock, ip_addr)
        if self.connections.has_key(sock.fileno()):
            self.connections[fileno].sock = sock
        else:
            self.connections[fileno] = conn
        self.epoll.modify(fileno, select.EPOLLOUT)

    def run(self):
        self.socket.listen(self.config.listen_max)
        self.socket.setblocking(0)
        self.epoll.register(self.socket.fileno(), select.EPOLLIN)

        try:
            while True:
                events = self.epoll.poll(self.config.epoll_interval)
                for fileno, event in events:
                    if fileno == self.socket.fileno():#accept the connection
                        connection, addr = self.socket.accept()
                        connection.setblocking(0)
                        self.epoll.register(connection.fileno(), select.EPOLLIN)
                        self.addConnection(connection, addr)
                    elif event & select.EPOLLIN:
                        conn = self.connections[fileno]
                        conn.receive()
                    elif event & select.EPOLLOUT:
                        conn = self.connections[fileno]
                        conn.send()
                        self.epoll.modify(fileno, select.EPOLLIN)
                    elif event & select.EPOLLHUP:
                        pass
        except:
            traceback.print_exc()
        finally:
            self.epoll.unregister(self.socket.fileno())
            self.epoll.close()
            self.socket.close()




