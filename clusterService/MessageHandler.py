__author__ = 'jimmy'

import platform
import time
import socket
import threading
import Queue
import traceback

from Machine import *
from ClusterMessage import *
from Util import *
from TransferFiles import *
from ResultAdapter import *


rootpath = os.path.dirname(os.path.realpath(sys.path[0]))
if not rootpath in sys.path:
    sys.path.append(rootpath)
from clientService.JobDispatcher import *
from clientService.BackgroundService import *
from analysis.policy import *
from analysis.NMFAnalysisService import *


class MessageHandler(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.queue = Queue.Queue()
        self.start()

    def run(self):
        while True:
            try:
                connection, message = self.queue.get()
                self.handleMessage(connection, message)
            except:
                traceback.print_exc()

    def handle(self, connection, message):
        if connection and message:
            self.queue.put([connection, message])

    def handleMessage(self, connection, message):
        pass


class ScanMessageHandler(MessageHandler):
    def __init__(self):
        super(ScanMessageHandler, self).__init__()

    def handleMessage(self, connection, message):
        machineInfos = collectMachineInfo()
        machine = Machine()
        machine.os_info = machineInfos['os_info']
        machine.ip_addr = machineInfos['ip_addr']
        machine.cpu_info = machineInfos['cpu_info']
        machine.mem_info = machineInfos['mem_info']
        machine.disk_info = machineInfos['disk_info']
        connection.enqueue(MachineInfoMessage(machine))


class MachineInfoHandler(MessageHandler):
    def __init__(self):
        super(MachineInfoHandler, self).__init__()

    def handleMessage(self, connection, message):
        machine = message.machine
        machine.fileno = str(connection.sock.fileno())
        connection.server.addMachine(machine)
        connection.server.addClientConnection(connection)


class PINGHandler(MessageHandler):
    def __init__(self):
        super(PINGHandler, self).__init__()

    def handleMessage(self, connection, message):
        connection.enqueue(PONGMessage())
        connection.active = True


class PONGHandler(MessageHandler):
    def __init__(self):
        super(PONGHandler, self).__init__()

    def handleMessage(self, connection, message):
        connection.last_read_time = int(time.time())


class QueryMachinesHandler(MessageHandler):
    def __init__(self):
        super(QueryMachinesHandler, self).__init__()

    def handleMessage(self, connection, message):
        machines = connection.server.machines.values()
        newMachines = []
        ips = message.machinesInfo['ips']
        aliveIps = []
        for machine in machines:
            aliveIps.append(machine.ip_addr)
            if machine.ip_addr in ips:
                continue
            newMachines.append(machine)
        deadIps = []
        for i in range(len(ips)):
            if ips[i] in aliveIps: continue
            deadIps.append(ips[i])
        deadMachines = {'ips': deadIps, }
        backMessage = AllMachinesInfoMessage(newMachines, deadMachines)
        connection.enqueue(backMessage)


class UploadRequestHandler(MessageHandler):
    def __init__(self):
        super(UploadRequestHandler, self).__init__()

    """
	1: frontend to server
	2: server to background client
    """

    def handleMessage(self, connection, message):
        dir = int(message.direction)
        if dir == 1:
            newMessage = UploadRequestMessage(2, message.sourceCodeId, connection.ip_addr, connection.sock.fileno())
            connection.server.switchToClient(message.switchFileno, newMessage)
        elif dir == 2:
            #TODO if source code exist do not transfer
            id = message.sourceCodeId
            if True:  #TODO can add agent local source code cache
                receiver = FileReceiver(rootpath + '/AllSource/ClientSourceCode')
                ip, port = receiver.prepareServer()
                receiver.start()
            else:
                ip = '0.0.0.0'
                port = -1
            newMessage = UploadResponseMessage(1, ip, port, message.switchFileno)
            connection.enqueue(newMessage)


class UploadResponseHandler(MessageHandler):
    def __init__(self):
        super(UploadResponseHandler, self).__init__()

    """
	1: background client to server
	2: server to frontend client
    """

    def handleMessage(self, connection, message):
        dir = int(message.direction)
        if dir == 1:
            newMessage = UploadResponseMessage(2, message.serverIp, message.serverPort, connection.sock.fileno())
            connection.server.switchToClient(message.switchFileno, newMessage)


class RunTestHandler(MessageHandler):
    def __init__(self):
        super(RunTestHandler, self).__init__()

    """
	1: frontend client to server
	2: server to background client
    """

    def handleMessage(self, connection, message):
        dir = int(message.direction)
        if dir == 1:
            dir = 2
            rPath = message.rPath
            target = message.target
            duration = message.duration
            repeat = message.repeat
            delaytime = message.delaytime
            sourceCodePath = message.sourceCodePath
            pid = int(message.pid)
            resultId = message.resultId
            fileno = connection.sock.fileno()
            newMessage = RunTestMessage(dir, rPath, target, duration, repeat, delaytime, sourceCodePath, pid, resultId,
                                        fileno)
            connection.server.switchToClient(message.switchFileno, newMessage)
        elif dir == 2:
            rPath = message.rPath
            target = message.target
            pid = message.pid
            sourcePath = message.sourceCodePath
            delaytime = int(message.delaytime)
            repeat = int(message.repeat)
            duration = int(message.duration)
            #TODO : Test
            sar = {'interval': duration, 'loops': repeat}
            pmu = {'duration': duration, 'loops': repeat, 'delay': delaytime}
            hotspots = {'duration': duration}
            perf = {'duration': duration, 'delay': delaytime}
            rmon = {'duration': duration}
            job = Job(path=rPath, source_path=sourcePath, pid=-1, sar_paras=sar, pmu_paras=pmu, hotspots_paras=hotspots,
                      perf_list_paras=perf, rmon_paras=rmon)
            connection.server.jobDispatcher.dispatch(job)
            #responseMessage = self.responseQueue.get()
            #if responseMessage:
            #    status = responseMessage['status']
            #    newMessage = TestSuccessMessage(1, status, message.resultId, message.switchFileno, rPath, 1, 'test',
            #                                    '/AllSource/ServerOutput', '/AllSource/ClientOutput')
            #    connection.enqueue(newMessage)


class TestSuccessHandler(MessageHandler):
    def __init__(self):
        super(TestSuccessHandler, self).__init__()
        self.receivers = {}

    """
	DIR:    1: background client to server
	        2: server to frontend client
        STEPS:  1: first receive try
                2: receive success
                3: receive fail
    """

    def handleMessage(self, connection, message):
        dir = int(message.direction)
        if dir == 1:
            if message.steps == '1':
                if message.status == 'done':
                    #ready to receive output from client
                    receiver = FileReceiver(rootpath + message.serverBasePath)
                    ip, port = receiver.prepareServer()
                    receiver.start()
                    self.receivers[message.resultId] = receiver
                    backNewMessage = UploadOutputResponseMessage(1, ip, port, message.switchFileno, message.rPath,
                                                                 message.resultId, 1, message.runType,
                                                                 message.clientBasePath)
                    connection.enqueue(backNewMessage)
                else:
                    #fail: not transfer output
                    newMessage = TestSuccessMessage(2, message.status, message.resultId, connection.sock.fileno(),
                                                    message.rPath)
                    connection.server.switchToClient(message.switchFileno, newMessage)
            elif message.steps == '2':  #success
                receiver = self.receivers[message.resultId]
                receiver.close()
                del self.receivers[message.resultId]
                #send test status to frontend
                newMessage = TestSuccessMessage(2, 'done', message.resultId, connection.sock.fileno(), message.rPath)
                connection.server.switchToClient(message.switchFileno, newMessage)
            elif message.steps == '3':  #fail
                receiver = self.receivers[message.resultId]
                receiver.close()
                del self.receivers[message.resultId]
                #send test status to frontend
                newMessage = TestSuccessMessage(2, 'fail', message.resultId, connection.sock.fileno(), message.rPath)
                connection.server.switchToClient(message.switchFileno, newMessage)


class UploadOutputResponseHandler(MessageHandler):
    def __init__(self):
        super(UploadOutputResponseHandler, self).__init__()

    """
	DIR: 1: server to background client
        STEPS: 1: first send try
    """

    def handleMessage(self, connection, message):
        dir = int(message.direction)
        if dir == 1:
            ip = message.serverIp
            port = message.serverPort
            rPath = message.rPath
            secondChance = False
            try:
                sender = FileSender(ip, port)
                sender.send(rootpath + message.clientBasePath, rPath)
            except:
                #traceback.print_exc()
                print 'CAN NOT CONNECT TO THE RECEIVER, TRY AGAIN'
                #send fail, second chance
                secondChance = True
            steps = 2  # default success
            if secondChance:
                try:
                    ip = connection.server.getServerIp()
                    sender = FileSender(ip, port)
                    sender.send(rootpath + message.clientBasePath, rPath)
                except:
                    traceback.print_exc()
                    print 'CAN NOT CONNECT TO THE RECEIVER, FAIL'
                    #send fail, no chance
                    steps = 3
            newMessage = TestSuccessMessage(1, 'done', message.resultId, message.switchFileno, message.rPath, steps,
                                            message.runType)
            connection.enqueue(newMessage)


class DeleteOutputHandler(MessageHandler):
    def __init__(self):
        super(DeleteOutputHandler, self).__init__()

    def handleMessage(self, connection, message):
        base = rootpath + '/' + message.basePath
        rPath = message.rPath
        deletePath(base, rPath)


class QueryResultsHandler(MessageHandler):
    def __init__(self):
        super(QueryResultsHandler, self).__init__()

    """
	results: [(tableName, compressTableName, [[metricsOrEventsNames1, datas1, data2....], ....]), ... ]
    """

    def handleMessage(self, connection, message):
        results = ResultAdapter().getResultsByEachTable(message.rPaths, message.tables, message.limits)
        newMessage = ResponseResultsMessage(results)
        connection.enqueue(newMessage)


class RegisterMachinesListenerHandler(MessageHandler):
    def __init__(self):
        super(RegisterMachinesListenerHandler, self).__init__()

    def handleMessage(self, connection, message):
        connection.server.register(message.ip, message.port)


class QueryOverviewsHandler(MessageHandler):
    def __init__(self):
        super(QueryOverviewsHandler, self).__init__()

    def handleMessage(self, connection, message):
        results = ResultAdapter().getOverviewResults(message.rPaths)
        newMessage = ResponseResultsMessage(results)
        connection.enqueue(newMessage)


class QueryAnalysisHandler(MessageHandler):
    policy_manager = PolicyManager()

    def __init__(self):
        super(QueryAnalysisHandler, self).__init__()

    def handleMessage(self, connection, message):
        r_paths = message.r_paths
        policy_name = message.policy_name
        policy = self.policy_manager.getPolicy(policy_name)

        if not policy:
            resp = ResponseResultsMessage(None)
            connection.enqueue(resp)
            return

        formula = None
        metrics = None
        if policy.realMetric == 'formula':
            formula = policy.formula
            metrics = policy.parameters
        else:
            metrics = [policy.realMetric]
        adapter = ResultAdapter()
        rawDatas = adapter.getAnalysisResult(r_paths, metrics, formula)
        datas = []
        for data in rawDatas:
            if data == None: data = 0
            min = policy.threshold_min
            max = policy.threshold_max
            suggestion = policy.getSuggestion(data)
            datas.append([data, min, max, suggestion])

        results = {'summary': policy.summary, 'datas': datas}
        resp = ResponseResultsMessage(results)
        connection.enqueue(resp)


class RunServiceHandler(MessageHandler):
    def __init__(self):
        super(RunServiceHandler, self).__init__()

    """
            direction : 0 FrontendAgentClient to server
                        1 Server to BackgroundClient
    """

    def enqueue(self, message):
        if message:
            self.responseQueue.put(message)

    def handleMessage(self, connection, message):
        direction = message.direction
        if direction == 0:
            switchFileno = message.serviceInfo[1]
            serviceInfo = message.serviceInfo
            serviceInfo[1] = connection.sock.fileno()
            newMessage = RunServiceMessage(serviceInfo, 1)
            connection.server.switchToClient(switchFileno, newMessage)
        elif direction == 1:
            self.backgroundService = BackgroundService(self)
            self.backgroundService.start()
            self.responseQueue = Queue.Queue()

            serviceInfo = message.serviceInfo
            rPath = serviceInfo[0]
            switchFileno = serviceInfo[1]
            totalDuration = serviceInfo[2]
            duration = serviceInfo[3]
            interval = serviceInfo[4]
            resultId = serviceInfo[5]
            service = ServiceTask(rPath, totalDuration, duration, interval)
            self.backgroundService.dispatch(service)
            responseMessage = self.responseQueue.get()
            if responseMessage:
                status = responseMessage['status']
                newMessage = TestSuccessMessage(1, status, resultId, switchFileno, rPath, 1, 'service',
                                                '/AllSource/ServerOutputService', '/AllSource/ClientOutputService')
                connection.enqueue(newMessage)


class QueryServiceResultsHandler(MessageHandler):
    def __init__(self):
        super(QueryServiceResultsHandler, self).__init__()

    def handleMessage(self, connection, message):
        rPath = message.rPath
        adapter = ResultAdapter()
        results = adapter.getNMFAnalysisServiceResults(rPath)
        resp = ResponseResultsMessage(results)
        connection.enqueue(resp)


class AnalysisServiceHandler(MessageHandler):
    def __init__(self):
        super(AnalysisServiceHandler, self).__init__()

    def handleMessage(self, connection, message):
        inputRPath = message.inputRPath
        outputRPath = message.outputRPath
        analysisType = message.type
        featuresCount = message.featuresCount
        analysisId = message.analysisId
        nMFAnalysis = NMFAnalysisService()
        nMFAnalysis.setParameters(inputRPath, outputRPath, featuresCount)
        status = nMFAnalysis.readAndAnalysisDatas()
        newMessage = None
        if status:
            newMessage = AnalysisSuccessMessage(analysisId, 'done')
        else:
            newMessage = AnalysisSuccessMessage(analysisId, 'undone')
        connection.enqueue(newMessage)


class QueryAResultOverviewHandler(MessageHandler):
    def __init__(self):
        super(QueryAResultOverviewHandler, self).__init__()

    def handleMessage(self, connection, message):
        rPath = message.rPath
        datas = ResultAdapter().getSingleResultOverview(rPath)
        newMessage = ResponseResultsMessage(datas)
        connection.enqueue(newMessage)

class QueryModelsResultsHandler(MessageHandler):
        def __init__(self):
                super(QueryModelsResultsHandler, self).__init__()

        def handleMessage(self, connection, message):
                rPath = message.rPath
                datas = ResultAdapter().getModelsAnalysisResults(rPath)
                newMessage = ResponseResultsMessage(datas)
                connection.enqueue(newMessage)

class StopHandler(MessageHandler):
        def __init__(self):
                super(StopHandler, self).__init__()

        def handleMessage(self, connection, message):
                direction = message.direction
                id = message.id
                fileno = message.fileno
                if direction == 0:
                        newMessage = StopMessage(1, id, connection.sock.fileno())
                        #newMessage = StopMessage(1, id, 99999)
                        connection.server.switchToClient(fileno, newMessage)
                elif direction == 1:
                        print 'client server id = ', id
                        server = connection.server
                        server.jobDispatcher.stopMonitor()
                        rMessage = server.response_queue.get()
                        status = rMessage['status']
                        rPath = rMessage['rPath']
                        newMessage = TestSuccessMessage(1, status, id, fileno, rPath, 1, 'test','/AllSource/ServerOutput', '/AllSource/ClientOutput')
                        connection.enqueue(newMessage)

class QueryDynamicOverviewHandler(MessageHandler):
        def __init__(self):
                super(QueryDynamicOverviewHandler, self).__init__()

        def handleMessage(self, connection, message):
                rPath = message.rPath
                qtables = message.qtables
                starts = message.starts
                next = message.next
                datas = ResultAdapter().getDynamicOverviewResults(rPath, qtables, starts, next)
                newMessage = ResponseResultsMessage(datas)
                connection.enqueue(newMessage)
                
        
