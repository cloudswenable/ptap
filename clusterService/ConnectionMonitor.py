import threading
import time
import traceback

class ConnectionMonitor(threading.Thread):
        def __init__(self, interval, server, connections): 
                threading.Thread.__init__(self)
                self.connections = connections
                self.server = server
                self.interval = interval

        def run(self):
                while True:
                        for connection in self.connections:
                                current = int(time.time())
                                if (current - connection.last_read_time) > self.interval:
                                        sock = connection.sock
                                        try:
                                                self.server.removeConnection(sock)
                                        except:
                                                traceback.print_exc()
                        time.sleep(3)
                                
