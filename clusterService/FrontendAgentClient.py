import socket
from MessageReceiver import *
from MessageHandler import *
from ClusterConfig import FrontendAgentClientConfig
import time
from TransferFiles import *
import os
import threading
import Queue
import traceback
import thread

basePath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
webBasePath = basePath + '/webServer'
if not webBasePath in sys.path:
	sys.path.insert(0, webBasePath)
os.environ['DJANGO_SETTINGS_MODULE'] = 'webServer.settings'
from showControler.models import Result, ServiceResult, ServiceAnalysis

class FrontendAgentSender(threading.Thread):
	serverName = 'FrontendAgentClient'
	def __init__(self):
		threading.Thread.__init__(self)
		self.config = FrontendAgentClientConfig()	
		self.serverIp = self.config.serverIp
		self.serverPort = self.config.serverPort
		self.parser = MessageParser()
		self.taskQueue = Queue.Queue()
		self.dispachMap = {1: self.runTest, 2: self.deleteOutput, 3: self.registerMachinesListener, 4: self.runService, 5:self.analysisService}

	def isCenterServer(self):
		return False

	def enqueue(self, task):
		self.taskQueue.put(task)

	def fetchMachines(self, machinesInfo):
		print 'fetch machines'
		machinesDict = []
		try:
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.sock.connect((self.serverIp, self.serverPort))
			message = QueryMachinesInfoMessage(machinesInfo)
			self.sock.send(message.toString())
			#need some change
			data = self.sock.recv(2048)
			message = self.parser.parse(data)
			for ma in message.machines:
				machine = {}
				machine['name'] = ma.name
				machine['mac'] = ma.mac
				machine['ip'] = ma.ip_addr
				machine['fileno'] = ma.fileno
				machine['os_info'] = ma.os_info
				machine['cpu_info'] = ma.cpu_info
				machine['mem_info'] = ma.mem_info
				machine['disk_info'] = ma.disk_info
				machine['ht'] = ma.ht
				machine['turbo'] = ma.turbo
				machinesDict.append(machine)
			self.sock.close()
		except: pass
		return machinesDict, message.deadMachines

	def runTest(self, parameters):#parameters : [p1, p2, ... ]
		rPath = parameters[0]
		target = parameters[1]
		duration = parameters[2]
		repeat = parameters[3]
		delaytime = parameters[4]
		sourceCodeId = parameters[5]
		ip = parameters[6]
		sourceCodePath = parameters[7]
		pid = parameters[8]
		resultId = parameters[9]
		switchFileno = parameters[10]
		print 'RUN TEST'
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.connect((self.serverIp, self.serverPort))
			
		#request upload source code and run test
		message = UploadRequestMessage(1, sourceCodeId, ip, switchFileno)
		self.sock.send(message.toString())
		data = self.sock.recv(1024)
		try:
			responseMessage = self.parser.parse(data)
			ip = responseMessage.serverIp
			port = responseMessage.serverPort
			if not int(port) == -1:
				sender = FileSender(ip, port)
				sender.send(basePath+'/AllSource/SourceCode/', sourceCodePath)
			runMessage = RunTestMessage(1, rPath, target, duration, repeat, delaytime, sourceCodePath, pid, resultId, switchFileno)
		        self.sock.send(runMessage.toString())
		        data = self.sock.recv(1024)
		        testSuccessMessage = self.parser.parse(data)
		        result = Result.objects.get(pk=int(testSuccessMessage.resultId))
		        if testSuccessMessage.status == 'done':
			        result.status = 'done'
		        else:
			        result.status = 'fail'
		        result.save()
		except: 
			traceback.print_exc()
		self.sock.close()

        def runService(self, parameters):
                print 'RUN SERVICE'    
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.connect((self.serverIp, self.serverPort))
                runMessage = RunServiceMessage(parameters, 0)
                self.sock.send(runMessage.toString())
                try:
                        data = self.sock.recv(1024)
                        testSuccessMessage = self.parser.parse(data)
                        result = ServiceResult.objects.get(pk=int(testSuccessMessage.resultId))
                        if testSuccessMessage.status == 'done':
                                result.status = 'done'
                        else:
                                result.status = 'fail'
                        result.save()
                except:
                        traceback.print_exc()
                self.sock.close()

        def analysisService(self, parameters):
                inputRPath = parameters[0]
                outputRPath = parameters[1]
                analysisType = parameters[2]
                featuresCount = parameters[3]
                analysisId = parameters[4]
                print 'ANALYSIS SERVICE'
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect((self.serverIp, self.serverPort))
                message = AnalysisServiceMessage(inputRPath, outputRPath, analysisType, featuresCount, analysisId)
                self.sock.send(message.toString())
                try:
                        data = self.sock.recv(1024)
                        analysisSuccessMessage = self.parser.parse(data)
                        analysis = ServiceAnalysis.objects.get(pk=int(analysisSuccessMessage.analysisId))
                        if analysisSuccessMessage.status == 'done':
                                analysis.status = 'done'
                        else:
                                analysis.status = 'fail'
                        analysis.save()
                except:
                        traceback.print_exc()
                self.sock.close()

	def deleteOutput(self, parameters):
		rPath = parameters[0]
                basePath = parameters[1]
		print 'DELETE OUTPUT'
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect((self.serverIp, self.serverPort))
		deleteMessage = DeleteOutputMessage(rPath, basePath)
		self.sock.send(deleteMessage.toString())
		self.sock.close()

        def query(self, message):
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect((self.serverIp, self.serverPort))
                self.sock.send(message.toString())
                data = self.sock.recv(8)
                type, msgLen = struct.unpack('ii', data)
                allDatas = data
                while msgLen > 0:
                        readLen = 1024
                        if msgLen < readLen: readLen = msgLen
                        tmpData = self.sock.recv(readLen)
                        allDatas += tmpData
                        msgLen -= len(tmpData)
                responseResultsMessage = self.parser.parse(allDatas)
                self.sock.close()
                return responseResultsMessage.results

        def queryModelsResults(self, parameters):
                rPath = parameters[0]
                print 'QUERY MODEL RESULTS'
                queryMessage = QueryModelsResultsMessage(rPath)
                return self.query(queryMessage)

        def queryAResultOverview(self, parameters):
                rPath = parameters[0]
                print 'QUERY A RESULT OVERVIEW'
                queryMessage = QueryAResultOverviewMessage(rPath)
                return self.query(queryMessage)

	def queryResults(self, parameters):
		rPaths = parameters[0]
		tableNames = parameters[1]
		limits = parameters[2]
		print 'QUERY RESULTS'
		queryMessage = QueryResultsMessage(rPaths, tableNames, limits)
                return self.query(queryMessage)

        def queryOverviews(self, parameters):
                rPaths = parameters[0]
                print 'QUERY OVERVIEWS'
                queryOverviewsMessage = QueryOverviewsMessage(rPaths)
		return self.query(queryOverviewsMessage)
        
        def queryAnalysis(self, parameters):
                rPaths = parameters[0]
                metricName = parameters[1]
                print 'QUERY ANALYSIS'
                queryAnalysisMessage = QueryAnalysisMessge(rPaths, metricName)
		return self.query(queryAnalysisMessage)

        def queryServiceResults(self, parameters):
                rPath = parameters[0]
                print 'QUERY SERVICE RESULTS'
                queryServiceResultsMessage = QueryServiceResultsMessage(rPath)
		return self.query(queryServiceResultsMessage)

	def registerMachinesListener(self, parameters):
		ip = parameters[0]
		port = parameters[1]
		print 'REGISTER MACHINES LISTENER'
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.connect((self.serverIp, self.serverPort))
		message = RegisterMachinesListenerMessage(ip, port)
		self.sock.send(message.toString())
		self.sock.close()
		
				
	def run(self):
		while True:
			try:
				task = self.taskQueue.get()
				print 'FrontendAgentSender run task : ', task
				type = task[0]
				parameters = task[1]
				#self.dispachMap[type](parameters)# one by one
				thread.start_new_thread(self.dispachMap[type], (parameters,))
			except:
				traceback.print_exc()
			

if __name__ == '__main__':
	client = FrontendAgentSender()
	print '++++++++++++++++++++++++ in main After client'

	
