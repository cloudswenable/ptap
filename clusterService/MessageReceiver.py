__author__ = 'jimmy'
from MessageParser import *
import traceback

class MessageReceiver(object):
    def __init__(self, sock):
        self.sock = sock
        self.parser = MessageParser()

    def receive(self):
	try: 
        	data = self.sock.recv(2048)
        	#TODO make sure completely received data from client
        	if data:
            		message = self.parser.parse(data)
            		return message
        	return None
	except:
		traceback.print_exc()
		return None
