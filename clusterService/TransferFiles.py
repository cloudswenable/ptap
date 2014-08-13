import socket 
import random
import struct
import os
import sys
import threading
from Util import *
import time

class FileReceiver(threading.Thread):
	def __init__(self, basePath, serverIp = None):
		threading.Thread.__init__(self)
		self.basePath = basePath
                self.serverIp = serverIp

	def prepareServer(self):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		portUsed = True
		port = 0
		while portUsed:
			try:
				portUsed = False
				port = random.randint(1024, 65535)
				self.sock.bind(('0.0.0.0', port))
			except:
				portUsed = True

		if self.serverIp: return (self.serverIp, port)

		ip = socket.gethostbyname(socket.gethostname())
                if ip == '127.0.0.1':
                        tmpIpList = socket.gethostbyname_ex(socket.gethostname())
                        if len(tmpIpList[2]) > 1:
                                ip = tmpIpList[2][1]
		return (ip, port)

	def run(self):
		self.sock.listen(1)
                while True:
		        clientSock, addr = self.sock.accept()
                        data = clientSock.recv(4)
                        type = struct.unpack('i', data)[0]
                        if not type: break
		        self.unSerialize(clientSock)
                self.sock.close()
        
        def close(self):
                self.sock.close()

	def unSerialize(self, cSock):
		data = cSock.recv(4)
		realPathLen = struct.unpack('i', data)[0]
                data = cSock.recv(4)
                fileDatasLenLen = struct.unpack('i', data)[0]
                data = cSock.recv(fileDatasLenLen)
		fileDatasLenStr = struct.unpack('%ss' % fileDatasLenLen, data)[0]
                fileDatasLen = int(fileDatasLenStr)
		data = cSock.recv(realPathLen)
		realPath = struct.unpack('%ss' % realPathLen, data)[0]

		paths = realPath.split('/')
		rPath = '/'.join(paths[:-1])
		fileName = paths[-1]
		desPath = createPaths(self.basePath, rPath)
		file = open(desPath+'/'+fileName, 'w')
		while fileDatasLen>0:
			readLen = 1024
			if fileDatasLen < readLen: readLen = fileDatasLen
			data = cSock.recv(readLen)
			file.write(data)
			fileDatasLen -= len(data) 
		file.close()
		cSock.send('WRITEDONE')

class FileSender:
	def __init__(self, serverIp, serverPort):
		self.serverIp = serverIp
		self.serverPort = int(serverPort)

	def serialize(self, basePath, rPath):
		#'file': 1; 'none':0
		path = basePath + '/' + rPath
		try:
			sendFiles = os.listdir(path)
		except:#no such dir break
		        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.connect((self.serverIp, self.serverPort))
                        data = struct.pack('i', 0)
			sock.send(data)
                        sock.close()
			return

		for file in sendFiles:
			realPath = basePath + '/' + rPath + '/' + file
			if os.path.isdir(realPath): 
				self.serialize(basePath, '/'+rPath+'/'+file)
				continue
			fileDatas = open(realPath).read()
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.connect((self.serverIp, self.serverPort))
			type = 1
			rPathLen = len('/'+rPath+'/'+file)
			fileDatasLen = len(fileDatas)
			data = struct.pack('ii', type, rPathLen)
			data += struct.pack('i%ss' % len(str(fileDatasLen)), len(str(fileDatasLen)), str(fileDatasLen))
			data += struct.pack('%ss' % rPathLen, str('/'+rPath+'/'+file))
                        
			sock.send(data)
			while fileDatasLen>0:
				readLen = 1024
				if fileDatasLen < readLen: readLen = fileDatasLen
				sock.send(fileDatas[:readLen])
				fileDatasLen -= readLen
				fileDatas = fileDatas[readLen:]
			backData = sock.recv(9)
			print backData
                        sock.close()

	def send(self, base, rPath):
		print 'FILESENDER CONNECT TO SERVER (', self.serverIp, ', ', self.serverPort, ')'
		self.serialize(base, rPath)
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((self.serverIp, self.serverPort))
                sock.send(struct.pack('i', 0))
                sock.close()
                print 'FILESENDER SEND FILES FINISHED'

def main():
	choice = sys.argv[1]
	if choice == 'server':
		print '++++++++++++ Receiver +++++++++++++++++++'
		rec = FileReceiver('/home/chao/perf-monitor-platform/clusterService/Target')
		ip, port = rec.prepareServer()
		print 'start server ip = ', ip , '  port = ', port
		rec.start()
		print 'server finished'
	elif choice == 'client':
		print '+++++++++++++ Sender ++++++++++++++++++++++'
		sen = FileSender(sys.argv[2], int(sys.argv[3]))
		sen.send('/home/chao/perf-monitor-platform/clusterService', '/Test')
		
	
if __name__ == '__main__':
	main()
		
