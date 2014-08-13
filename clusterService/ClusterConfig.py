__author__ = 'jimmy'

import ConfigParser
import os

cur_dir = os.path.dirname(os.path.realpath(__file__))

class ServerConfig(object):
    	def __init__(self):
		self.config = ConfigParser.ConfigParser()
        	conf_file = open(cur_dir + "/config/server.cfg")
        	self.config.readfp(conf_file)
        	self.bind_addr = self.config.get('basic', 'bind_addr')
        	self.bind_port = int (self.config.get('basic', 'bind_port'))
        	self.epoll_interval = float(self.config.get('basic', 'epoll_interval'))
        	self.listen_max = int(self.config.get('basic', 'listen_max'))
                self.interval = int(self.config.get('basic', 'interval'))

class AgentClientConfig(object):
	def __init__(self):
        	self.config = ConfigParser.ConfigParser()
        	confFile = open(cur_dir + '/config/agentclient.cfg', 'r')
        	self.config.readfp(confFile)
        	self.server_ip = self.config.get('remote-server', 'server_ip')
        	self.server_port = int(self.config.get('remote-server', 'server_port'))

        	self.heartbeat_interval = int(self.config.get('heartbeat-checker', 'interval'))

class FrontendAgentClientConfig(object):
	def __init__(self):
		self.config = ConfigParser.ConfigParser()
		confFile = open(cur_dir + '/config/frontendagentclient.cfg', 'r')
		self.config.readfp(confFile)
		self.serverIp = self.config.get('remote-server', 'server_ip')
		self.serverPort = int(self.config.get('remote-server', 'server_port'))
