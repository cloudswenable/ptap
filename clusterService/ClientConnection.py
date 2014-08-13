__author__ = 'jimmy'

from MessageSender import *
from MessageReceiver import *
from ClusterMessage import *
from MessageHandler import *
import Queue
import select

class ClientConnection(object):
    def __init__(self, server, sock, ip_addr):
        self.sock = sock
        self.ip_addr = ip_addr
        self.active = False
        self.send_queue = Queue.Queue()
        self.receiver = MessageReceiver(self.sock)
        self.sender = MessageSender(self.sock)
        self.handler = MessageHandler()
        self.server = server
        self.last_read_time = 0


    def receive(self):
        message = self.receiver.receive()
        if message:
	    print 'SERVER %s , RECEIVE FROM %s MESSAGE %s' % (self.server.serverName, self.sock.fileno(), repr(message.body))
            self.last_read_time = int(time.time())
            self.server.enqueue((self, message))
	elif self.server.isCenterServer():
	    self.server.removeConnection(self.sock)

    def send(self):
        try:
            message = self.send_queue.get(block=False, timeout=0.5)
	    print 'SERVER %s, SEND TO %s MESSAGE %s' % (self.server.serverName, self.sock.fileno(), repr(message.body))
            if message:
                self.sock.send(message.toString())
        except Exception as e:
            pass

    def enqueue(self, message):
        self.send_queue.put(message)
        self.server.epoll.modify(self.sock.fileno(), select.EPOLLIN | select.EPOLLOUT)

    def sendScanMessage(self):
        message = ScanMachineMessage(self.ip_addr)
        self.enqueue(message)

    def sendMachineInfo(self):
        machineInfos = collectMachineInfo()
        machine = Machine()
	machine.name = machineInfos['name']
        machine.os_info = machineInfos['os_info']
        machine.ip_addr = machineInfos['ip_addr']
        machine.cpu_info = machineInfos['cpu_info']
        machine.mem_info = machineInfos['mem_info']
        machine.disk_info = machineInfos['disk_info']
	self.enqueue(MachineInfoMessage(machine))

    def close(self):
	self.sock.close()

