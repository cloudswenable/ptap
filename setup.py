#!/usr/bin/python 
import sys
import os
import re
import subprocess

curr_dir = os.path.abspath(os.path.dirname(__file__))

def run(comm):
	flag = subprocess.call(comm, shell=True)
	if flag:
		print 'Error: runing >>', comm

print '+++++++++++++++++++setup++++++++++++++++++++++++++++'
if len(sys.argv)<3:
	print 'Enter mysql username and password: '
	print 'such as : "./setup.py root 12345"'
	sys.exit(1)
user = sys.argv[1]
passwd = sys.argv[2]

#set settings.py
settingFilePath = curr_dir + '/webServer/webServer/settings.py'
settingFile = open(settingFilePath, 'r')
context = settingFile.read()
settingFile.close()

context, n = re.subn("'USER': '.+'", "'USER': '%s'" % user, context)
context, n = re.subn("'PASSWORD': '.+'", "'PASSWORD': '%s'" % passwd, context)

targetFile = open(settingFilePath, 'w')
targetFile.write(context)
targetFile.close()

#initialize database
syncdbComm = 'python %s/webServer/manage.py syncdb' % curr_dir
run(syncdbComm)

#insert vitual machine(used in the future)
#serverPath = curr_dir
#if not serverPath in sys.path:
#	sys.path.append(serverPath)
#os.environ['DJANGO_SETTINGS_MODULE'] = 'webServer.webServer.settings'
#from webServer.showControler.models import Machine
#all = Machine.objects.all()
#if not all:
#	machine = Machine(name='machine 1', microarchitecture='snb-ep', type='exon')
#	machine.save()
#	machine = Machine(name='machine 2', microarchitecture='snb-ep', type='core')
#	machine.save()
#	machine = Machine(name='machine 3', microarchitecture='snb-ep', type='intel')
#	machine.save()

#initialize rabbitmq
#run('sudo rabbitmqctl stop_app')
#run('sudo rabbitmqctl reset')
#run('sudo rabbitmqctl start_app')
#run('sudo rabbitmqctl add_user root root')
#run('sudo rabbitmqctl set_permissions -p / root ".*" ".*" ".*"')

