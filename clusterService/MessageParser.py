__author__ = 'jimmy'

import struct
from ClusterMessage import *
from Machine import *
import json


class MessageParser(object):
    def parseMachine(self, buffer):

        fmtLen = struct.unpack('i', buffer[0: 4])[0]
        fmtStr = struct.unpack('%ss' % (fmtLen), buffer[4: 4 + fmtLen])[0]
        machine = Machine()
        machine.fromString(fmtStr, buffer[4 + fmtLen:])
        return machine

    def parse(self, buffer):
        type, msgLen = struct.unpack('ii', buffer[0:8])
        message = None
        if type == 0:
            message = PINGMessage()
        elif type == 1:
            message = PONGMessage()
        elif type == 3:
            ipAddr = struct.unpack('%ss' % (msgLen), buffer[8:])
            message = ScanMachineMessage(ipAddr)
        elif type == 4:
            machine = self.parseMachine(buffer[8:])
            message = MachineInfoMessage(machine)
        elif type == 5:
            tmpbuffer = buffer[8:]
            machinesInfo = json.loads(tmpbuffer)
            message = QueryMachinesInfoMessage(machinesInfo)
        elif type == 6:
            count = struct.unpack('i', buffer[8:12])[0]
            tmpbuffer = buffer[12:]
            machines = []
            for i in range(count):
                nextLen = struct.unpack('i', tmpbuffer[0:4])[0]
                machine = self.parseMachine(tmpbuffer[4:])
                machines.append(machine)
                tmpbuffer = tmpbuffer[4 + nextLen:]
            deadMachines = json.loads(tmpbuffer)
            message = AllMachinesInfoMessage(machines, deadMachines)
        elif type == 7:
            tmpbuffer = buffer[8:]
            dirLen = struct.unpack('i', tmpbuffer[0:4])[0]
            dir = struct.unpack('%ss' % dirLen, tmpbuffer[4:4 + dirLen])[0]
            tmpbuffer = tmpbuffer[4 + dirLen:]
            sourceCodeIdLen = struct.unpack('i', tmpbuffer[0:4])[0]
            sourceCodeId = struct.unpack('%ss' % sourceCodeIdLen, tmpbuffer[4:4 + sourceCodeIdLen])[0]
            tmpbuffer = tmpbuffer[4 + sourceCodeIdLen:]
            ipLen = struct.unpack('i', tmpbuffer[0:4])[0]
            ip = struct.unpack('%ss' % ipLen, tmpbuffer[4:4 + ipLen])[0]
            tmpbuffer = tmpbuffer[4 + ipLen:]
            filenoLen = struct.unpack('i', tmpbuffer[0:4])[0]
            fileno = struct.unpack('%ss' % filenoLen, tmpbuffer[4:])[0]
            message = UploadRequestMessage(dir, sourceCodeId, ip, fileno)
        elif type == 8:
            tmpbuffer = buffer[8:]
            dirLen = struct.unpack('i', tmpbuffer[0:4])[0]
            dir = struct.unpack('%ss' % dirLen, tmpbuffer[4:4 + dirLen])[0]
            tmpbuffer = tmpbuffer[4 + dirLen:]
            ipLen = struct.unpack('i', tmpbuffer[0:4])[0]
            ip = struct.unpack('%ss' % ipLen, tmpbuffer[4:4 + ipLen])[0]
            tmpbuffer = tmpbuffer[4 + ipLen:]
            portLen = struct.unpack('i', tmpbuffer[0:4])[0]
            port = struct.unpack('%ss' % portLen, tmpbuffer[4:4 + portLen])[0]
            tmpbuffer = tmpbuffer[4 + portLen:]
            filenoLen = struct.unpack('i', tmpbuffer[0:4])[0]
            fileno = struct.unpack('%ss' % filenoLen, tmpbuffer[4:4 + filenoLen])[0]
            message = UploadResponseMessage(dir, ip, port, fileno)
        elif type == 9:
            tmpbuffer = buffer[8:]
            values = []
            for i in range(10):
                tmpLen = struct.unpack('i', tmpbuffer[0: 4])[0]
                tmp = struct.unpack('%ss' % tmpLen, tmpbuffer[4: 4 + tmpLen])[0]
                tmpbuffer = tmpbuffer[4 + tmpLen:]
                values.append(tmp)
            message = RunTestMessage(values[0], values[1], values[2], values[3], values[4], values[5], values[6],
                                     values[7], values[8], values[9])
        elif type == 10:
            tmpbuffer = buffer[8:]
            values = []
            for i in range(9):
                tmpLen = struct.unpack('i', tmpbuffer[0: 4])[0]
                tmp = struct.unpack('%ss' % tmpLen, tmpbuffer[4: 4 + tmpLen])[0]
                tmpbuffer = tmpbuffer[4 + tmpLen:]
                values.append(tmp)
            message = TestSuccessMessage(values[0], values[1], values[2], values[3], values[4], values[5], values[6], values[7], values[8])
        elif type == 11:
            tmpbuffer = buffer[8:]
            values = []
            for i in range(9):
                tmpLen = struct.unpack('i', tmpbuffer[0: 4])[0]
                tmp = struct.unpack('%ss' % tmpLen, tmpbuffer[4: 4 + tmpLen])[0]
                tmpbuffer = tmpbuffer[4 + tmpLen:]
                values.append(tmp)
            message = UploadOutputResponseMessage(values[0], values[1], values[2], values[3], values[4], values[5], values[6], values[7], values[8])
        elif type == 12:
            tmpbuffer = buffer[8:]
            rPathLen = struct.unpack('i', tmpbuffer[0:4])[0]
            rPath = struct.unpack('%ss' % rPathLen, tmpbuffer[4: 4 + rPathLen])[0]
            tmpbuffer = tmpbuffer[4+rPathLen:]
            basePathLen = struct.unpack('i', tmpbuffer[0:4])[0]
            basePath = struct.unpack('%ss' % basePathLen, tmpbuffer[4: 4 + basePathLen])[0]
            message = DeleteOutputMessage(rPath, basePath)
        elif type == 13:
            tmpbuffer = buffer[8:]
            count = struct.unpack('i', tmpbuffer[0:4])[0]
            rPaths = []
            tmpbuffer = tmpbuffer[4:]
            for i in range(count):
                tmpLen = struct.unpack('i', tmpbuffer[0: 4])[0]
                tmp = struct.unpack('%ss' % tmpLen, tmpbuffer[4: 4 + tmpLen])[0]
                tmpbuffer = tmpbuffer[4 + tmpLen:]
                rPaths.append(tmp)
            tables = []
            limits = []
            count = struct.unpack('i', tmpbuffer[0:4])[0]
            tmpbuffer = tmpbuffer[4:]
            for i in range(count):
                tmpLen = struct.unpack('i', tmpbuffer[0:4])[0]
                tmp = struct.unpack('%ss' % tmpLen, tmpbuffer[4: 4 + tmpLen])[0]
                tmpbuffer = tmpbuffer[4 + tmpLen:]
                start, end = struct.unpack('ii', tmpbuffer[0:8])
                limits.append((start, end))
                tmpbuffer = tmpbuffer[8:]
                tables.append(tmp)
            message = QueryResultsMessage(rPaths, tables, limits)
        elif type == 14:
            tmpbuffer = buffer[8:]
            results = json.loads(tmpbuffer)
            message = ResponseResultsMessage(results)
        elif type == 15:
            tmpbuffer = buffer[8:]
            ip, port = json.loads(tmpbuffer)
            message = RegisterMachinesListenerMessage(ip, port)
        elif type == 16:
            tmpbuffer = buffer[8:]
            rPaths = json.loads(tmpbuffer)
            message = QueryOverviewsMessage(rPaths)
        elif type == 17:
            tmp_buffer = buffer[8:]
            r_paths, policy_name = json.loads(tmp_buffer)
            message = QueryAnalysisMessge(r_paths, policy_name)
        elif type == 18:
            tmp_buffer = buffer[8:]
            dir, serviceInfo = json.loads(tmp_buffer)
            message = RunServiceMessage(serviceInfo, dir)
        elif type == 19:
            tmp_buffer = buffer[8:]
            rPath = json.loads(tmp_buffer)
            message = QueryServiceResultsMessage(rPath)
        elif type == 20:
            tmp_buffer = buffer[8:]
            inputRPath, outputRPath, analysisType, featuresCount, analysisId = json.loads(tmp_buffer)
            message = AnalysisServiceMessage(inputRPath, outputRPath, analysisType, featuresCount, analysisId)
        elif type == 21:
            tmp_buffer = buffer[8:]
            analysisId, status = json.loads(tmp_buffer)
            message = AnalysisSuccessMessage(analysisId, status)
        elif type == 22:
            tmp_buffer = buffer[8:]
            rPath = json.loads(tmp_buffer)[0]
            message = QueryAResultOverviewMessage(rPath)
        elif type == 23:
            tmp_buffer = buffer[8:]
            rPath = json.loads(tmp_buffer)[0]
            message = QueryModelsResultsMessage(rPath)

        return message


'''
machine = Machine()
machine.cpu_info = 'intel'
machine.os_info = 'linux'
machine.ip_addr = '10.238.145.56'
machine.disk_info = '16t'
machine.mem_info = '4g'
machine.mac = '0010103030310'
machine.ht = True
machine.turbo = False
message = MachineInfoMessage(machine.toString())
#message = ScanMachineMessage('10.238.1.1')
buf = message.toString()
parser = MessageParser()
parser.parse(buf)
'''
