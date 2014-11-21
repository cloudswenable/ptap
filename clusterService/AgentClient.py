__author__ = 'jimmy'
import socket
import select
from MessageReceiver import *
from MessageHandler import *
import threading
import Queue
import time
from ClientConnection import *
from Dispatcher import *
from ClusterConfig import *
#from EventManager import *
import traceback

class Task(object):
    def __init__(self, checker, execution):
        self.interval = checker.check_interval
        self.checker = checker
        self.connection = checker.connection
        self.execution = execution

    def check(self):
        current = int(time.time())
        if self.connection.last_read_time > current - self.interval:
            self.checker.enqueue(Task(self.checker, self.connection.last_read_time + self.interval))
            return
        elif self.connection.last_read_time > current - 2 * self.interval:
            self.connection.enqueue(PINGMessage())
            self.checker.enqueue(Task(self.checker, current + self.interval))
            return
        else:
            print "not receive the pong message"
            self.connection.close()

    def run(self):
        delay = self.execution - int(time.time())
        threading.Timer(delay, self.check, ()).start()

class HeartBeatChecker(threading.Thread):
    def __init__(self, connection, interval):
        threading.Thread.__init__(self)
        self.connection = connection
        self.queue = Queue.Queue()
        self.check_interval = interval

    def enqueue(self, task):
        self.queue.put(task)

    def run(self):
        print "start check"
        while True:
            task = self.queue.get()
            task.run()


class AgentClient(threading.Thread):
    serverName = 'AgentClient'
    def __init__(self):
	super(AgentClient, self).__init__()
        self.config = AgentClientConfig()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip_addr = self.config.server_ip
        self.port = self.config.server_port
        self.receiver = MessageReceiver(self.sock)
        self.handler = ScanMessageHandler()
        self.connection = ClientConnection(self, self.sock, self.ip_addr)
        self.checker = HeartBeatChecker(self.connection, self.config.heartbeat_interval)
        self.epoll = select.epoll()
        self.dispatch_queue = Queue.Queue()
        self.dispatcher = Dispatcher(self.dispatch_queue)
        self.response_queue = Queue.Queue()
        self.jobDispatcher = JobDispatcher(self.response_queue)

    def getServerIp(self):
        return self.ip_addr

    def isCenterServer(self):
	return False

    def run(self):
        print "start serve"
        self.sock.connect((self.ip_addr, self.port))
        self.sock.setblocking(0)
        self.epoll.register(self.sock.fileno(), select.EPOLLOUT)
	self.connection.sendMachineInfo()

        try:
            while True:
                events = self.epoll.poll(2)
                for fileno, event in events:
                    if fileno != self.sock.fileno():
                        print "not current connection"
                        pass
                    elif event & select.EPOLLIN:
                        self.connection.receive()
                    elif event & select.EPOLLOUT:
                        self.connection.send()
			self.epoll.modify(self.sock.fileno(), select.EPOLLIN)
                    else:
                        pass
        except:
            traceback.print_exc()
        finally:
            self.epoll.unregister(self.sock.fileno())
            self.epoll.close()
            self.sock.close()

    def start_other(self):
        if self.connection.last_read_time == 0:
            self.connection.last_read_time = int(time.time())
        task = Task(self.checker, self.connection.last_read_time + self.config.heartbeat_interval)
        self.checker.enqueue(task)
        self.checker.start()

        self.dispatcher.start()
        self.jobDispatcher.start()

        #daemon_thread = threading.Thread(target=self.serve())
        #daemon_thread.start()

        #self.event_manager.genForCurrent()


    def enqueue(self, message):
	self.dispatch_queue.put(message)

if __name__ == '__main__':
    client = AgentClient()
    client.start_other()
    client.start()
    #client.event_manager.genForCurrent()
