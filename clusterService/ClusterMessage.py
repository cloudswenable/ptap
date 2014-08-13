__author__ = 'jimmy'

import struct
import json

class ClusterMessage(object):
	'''
	    message type: 0 "PING"
         	         1 "PONG"
                	 2 "TESTJOB"
              	    	 3 "SCANMACHINE"
                  	 4 "MACHINEINFO"
		  	 5 "QueryMachinesInfoMessage"
			 6 "AllMachinesInfoMessage"
			 7 "UploadRequestMessage"
			 8 "UploasResponseMessage"
			 9 "RunTestMessage"
			 10 "TestSuccessMessage"
			 11 "UploadOutputResponseMessage"
			 12 "DeleteOutputMessage"
			 13 "QueryResultsMessage"
                         14 "ResponseResultMessage"
                         15 "RegisterMachinesListenerMessage"
                         16 "QueryOverviewsMessage"
                         17 "QueryAnalysisMessge"
                         18 "RunServiceMessage"
                         19 "QueryServiceResultsMessage"
                         20 "AnalysisServiceMessage"
                         21 "AnalysisSuccessMessage"
                         22 "QueryAResultOverviewMessage"
                         23 "QueryModelsResultsMessage"
    	'''
	def __init__(self, type=0):
        	self.type = type
        	self.body=''
        	self.msg_len=0

	def toString(self):
        	fmt = 'ii%ss'% (self.msg_len)
		messageStr = struct.pack(fmt, self.type, self.msg_len, self.body)
        	return messageStr


class PINGMessage(ClusterMessage):
	def __init__(self):
        	ClusterMessage.__init__(self, 0)
        	self.body += "ping"
        	self.msg_len = 4

class PONGMessage(ClusterMessage):
	def __init__(self):
        	ClusterMessage.__init__(self, 1)
        	self.body += "pong"
        	self.msg_len = 4

class ScanMachineMessage(ClusterMessage):
	def __init__(self, ip_addr):
        	ClusterMessage.__init__(self, 3)
        	self.body = ip_addr[0]
        	self.msg_len = len(self.body)

class MachineInfoMessage(ClusterMessage):
	def __init__(self, machine):
        	ClusterMessage.__init__(self, 4)
        	self.machine = machine
        	self.body = machine.toString()
        	self.msg_len = len(self.body)

class QueryMachinesInfoMessage(ClusterMessage):
	def __init__(self, machinesInfo):
		ClusterMessage.__init__(self, 5)
		self.machinesInfo = machinesInfo
		
		tmp = json.dumps(self.machinesInfo)
		self.body = tmp
		self.msg_len = len(self.body)

class AllMachinesInfoMessage(ClusterMessage):
	def __init__(self, machines, deadMachines):
		ClusterMessage.__init__(self, 6)
		self.machines = machines
		self.deadMachines = deadMachines

		tmpbody = ''
		size = 0
		for machine in machines:
			tmp = machine.toString()
			tmpbody += struct.pack('i%ss' % len(tmp), len(tmp), tmp)
		count = len(machines)
		tmp = struct.pack('i%ss' % len(tmpbody), count, tmpbody)
		tmp += json.dumps(self.deadMachines)
		self.body = tmp
		self.msg_len = len(self.body)

class UploadRequestMessage(ClusterMessage):
	def __init__(self, dir, sourceCodeId, ip, fileno):
		ClusterMessage.__init__(self, 7)
		self.direction = str(dir)
		self.sourceCodeId = str(sourceCodeId)
		self.ip = ip
		self.switchFileno = fileno
		tmp = struct.pack('i%ss' % len(self.direction), len(self.direction), self.direction)
		tmp += struct.pack('i%ss' % len(self.sourceCodeId), len(self.sourceCodeId), self.sourceCodeId)
		tmp += struct.pack('i%ss' % len(self.ip), len(self.ip), str(self.ip))
		tmp += struct.pack('i%ss' % len(str(self.switchFileno)), len(str(self.switchFileno)), str(self.switchFileno))
		self.body = tmp
		self.msg_len = len(tmp)
	
class UploadResponseMessage(ClusterMessage):
	def __init__(self, dir, ip, port, fileno):
		ClusterMessage.__init__(self, 8)
		self.direction = str(dir)
		self.serverIp = ip
		self.serverPort = str(port)
		self.switchFileno = str(fileno)
		tmp = struct.pack('i%ss' % len(self.direction), len(self.direction), self.direction)
		tmp += struct.pack('i%ss' % len(self.serverIp), len(self.serverIp), self.serverIp)
		tmp += struct.pack('i%ss' % len(self.serverPort), len(self.serverPort), self.serverPort)
		tmp += struct.pack('i%ss' % len(self.switchFileno), len(self.switchFileno), self.switchFileno)
		self.body = tmp
		self.msg_len = len(tmp)

class RunTestMessage(ClusterMessage):
	def __init__(self, dir, rPath, target, duration, repeat, delaytime, sourceCodePath, pid, resultId, fileno):
		ClusterMessage.__init__(self, 9)
		self.direction = str(dir)
		self.rPath = str(rPath)
		self.target = str(target)
		self.duration = str(duration) 
		self.repeat = str(repeat)
		self.delaytime = str(delaytime)
		self.sourceCodePath = str(sourceCodePath)
		self.pid = str(pid)
		self.resultId = str(resultId)
		self.switchFileno = str(fileno)

		tmp = struct.pack('i%ss' % len(self.direction), len(self.direction), self.direction)
		tmp += struct.pack('i%ss' % len(self.rPath), len(self.rPath), self.rPath)
		tmp += struct.pack('i%ss' % len(self.target), len(self.target), self.target)
		tmp += struct.pack('i%ss' % len(self.duration), len(self.duration), self.duration)
		tmp += struct.pack('i%ss' % len(self.repeat), len(self.repeat), self.repeat)
		tmp += struct.pack('i%ss' % len(self.delaytime), len(self.delaytime), self.delaytime)
		tmp += struct.pack('i%ss' % len(self.sourceCodePath), len(self.sourceCodePath), self.sourceCodePath)
		tmp += struct.pack('i%ss' % len(self.pid), len(self.pid), self.pid)
		tmp += struct.pack('i%ss' % len(self.resultId), len(self.resultId), self.resultId)
		tmp += struct.pack('i%ss' % len(self.switchFileno), len(self.switchFileno), self.switchFileno)
		self.body = tmp
		self.msg_len = len(tmp)

class TestSuccessMessage(ClusterMessage):
	def __init__(self, dir, status, resultId, fileno, rPath, steps=1, runType='test', serverBasePath='', clientBasePath=''):
		ClusterMessage.__init__(self, 10)
		self.direction = str(dir)
		self.status = status
		self.resultId = str(resultId)
		self.switchFileno = str(fileno)
		self.rPath = str(rPath)
                self.steps = str(steps)
                self.runType = runType
                self.serverBasePath = str(serverBasePath)
                self.clientBasePath = str(clientBasePath)
		
		tmp = struct.pack('i%ss' % len(self.direction), len(self.direction), self.direction)
		tmp += struct.pack('i%ss' % len(self.status), len(self.status), self.status)
		tmp += struct.pack('i%ss' % len(self.resultId), len(self.resultId), self.resultId)
		tmp += struct.pack('i%ss' % len(self.switchFileno), len(self.switchFileno), self.switchFileno)
		tmp += struct.pack('i%ss' % len(self.rPath), len(self.rPath), self.rPath)
                tmp += struct.pack('i%ss' % len(self.steps), len(self.steps), self.steps)
                tmp += struct.pack('i%ss' % len(self.runType), len(self.runType), self.runType)
                tmp += struct.pack('i%ss' % len(self.serverBasePath), len(self.serverBasePath), self.serverBasePath)
                tmp += struct.pack('i%ss' % len(self.clientBasePath), len(self.clientBasePath), self.clientBasePath)
		self.body = tmp
		self.msg_len = len(tmp)
			
class UploadOutputResponseMessage(UploadResponseMessage):
	def __init__(self, dir, ip, port, fileno, rPath, resultId, steps=1, runType='test', clientBasePath=''):
		UploadResponseMessage.__init__(self, dir, ip, port, fileno)
		self.rPath = str(rPath)
		self.type = 11
		self.resultId = resultId
                self.steps = str(steps)
                self.runType = runType
                self.clientBasePath = clientBasePath
		
		tmp = self.body
		tmp += struct.pack('i%ss' % len(self.rPath), len(self.rPath), self.rPath)
		tmp += struct.pack('i%ss' % len(self.resultId), len(self.resultId), self.resultId)
                tmp += struct.pack('i%ss' % len(self.steps), len(self.steps), self.steps)
                tmp += struct.pack('i%ss' % len(self.runType), len(self.runType), self.runType)
                tmp += struct.pack('i%ss' % len(self.clientBasePath), len(self.clientBasePath), self.clientBasePath)
		self.body = tmp
		self.msg_len = len(tmp)

class DeleteOutputMessage(ClusterMessage):
	def __init__(self, rPath, basePath):
		ClusterMessage.__init__(self, 12)
		self.rPath = str(rPath)
                self.basePath = str(basePath)
		
		tmp = struct.pack('i%ss' % len(self.rPath), len(self.rPath), self.rPath)
		tmp += struct.pack('i%ss' % len(self.basePath), len(self.basePath), self.basePath)
                self.body = tmp
		self.msg_len = len(self.body)

class QueryResultsMessage(ClusterMessage):
	def __init__(self, rPaths, tables, limits):
		ClusterMessage.__init__(self, 13)
		self.rPaths = rPaths
		self.tables = tables
		self.limits = limits
		tmp = struct.pack('i', len(self.rPaths))
		for rPath in rPaths:
			tmp += struct.pack('i%ss' % len(str(rPath)), len(str(rPath)), str(rPath))
		tmp += struct.pack('i', len(self.tables))
		for i in range(len(tables)):
			tmp += struct.pack('i%ss' %  len(str(tables[i])), len(str(tables[i])), str(tables[i]))
			tmp += struct.pack('ii', int(limits[i][0]), int(limits[i][1]))
		self.body = tmp
		self.msg_len = len(self.body)

class ResponseResultsMessage(ClusterMessage):
	def __init__(self, results):
		ClusterMessage.__init__(self, 14)
		self.results = results
		
		tmp = json.dumps(self.results)
		self.body = tmp
		self.msg_len = len(self.body)	

class RegisterMachinesListenerMessage(ClusterMessage):
	def __init__(self, ip, port):
		ClusterMessage.__init__(self, 15)
		self.ip = ip
		self.port = int(port)

		tmp = json.dumps([self.ip, self.port])
		self.body = tmp
		self.msg_len = len(self.body)

class QueryOverviewsMessage(ClusterMessage):
        def __init__(self, rPaths):
                ClusterMessage.__init__(self, 16)
                self.rPaths = rPaths
                tmp = json.dumps(self.rPaths)
                self.body = tmp
                self.msg_len = len(self.body)


class QueryAnalysisMessge(ClusterMessage):

    def __init__(self, r_paths, policy_name):
        ClusterMessage.__init__(self, 17)
        self.r_paths = r_paths
        self.policy_name = policy_name
        data = json.dumps([self.r_paths, self.policy_name])
        self.body = data
        self.msg_len = len(self.body)

class RunServiceMessage(ClusterMessage):

    def __init__(self, serviceInfo, direction):
        ClusterMessage.__init__(self, 18)
        self.serviceInfo = serviceInfo
        self.direction = direction
        
        tmp = json.dumps([self.direction, self.serviceInfo])
        self.body = tmp
        self.msg_len = len(self.body)
        
class QueryServiceResultsMessage(ClusterMessage):
    def __init__(self, rPath):
        ClusterMessage.__init__(self, 19)
        self.rPath = rPath 
        
        tmp = json.dumps(self.rPath)
        self.body = tmp
        self.msg_len = len(self.body)

class AnalysisServiceMessage(ClusterMessage):
    def __init__(self, inputRPath, outputRPath, analysisType, featuresCount, analysisId):
        ClusterMessage.__init__(self, 20)
        self.inputRPath = inputRPath
        self.outputRPath = outputRPath
        self.analysisType = analysisType
        self.featuresCount = featuresCount
        self.analysisId = analysisId
        
        tmp = json.dumps([self.inputRPath, self.outputRPath, self.analysisType, self.featuresCount, self.analysisId])
        self.body = tmp
        self.msg_len = len(self.body)

class AnalysisSuccessMessage(ClusterMessage):
    def __init__(self, analysisId, status):
        ClusterMessage.__init__(self, 21)
        self.analysisId = analysisId
        self.status = status

        tmp = json.dumps([self.analysisId, self.status])
        self.body = tmp
        self.msg_len = len(self.body)

class QueryAResultOverviewMessage(ClusterMessage):
    def __init__(self, rPath):
        ClusterMessage.__init__(self, 22)
        self.rPath = rPath
        tmp = json.dumps([rPath])
        self.body = tmp
        self.msg_len = len(self.body)
class QueryModelsResultsMessage(ClusterMessage):
    def __init__(self, rPath):
        ClusterMessage.__init__(self, 23)
        self.rPath = rPath
        tmp = json.dumps([rPath])
        self.body = tmp
        self.msg_len = len(self.body)
