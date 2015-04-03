#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import os
import re
import shutil
import json

from showControler.models import *

rootpath = os.path.dirname(os.path.realpath(sys.path[0]))
if not rootpath in sys.path:
        sys.path.append(rootpath)
from clusterService.FrontendAgentClient import *

##############################################
############# Frontend Client and Server #####
##############################################
frontendAgent = FrontendAgentSender()
frontendAgent.start()

##############################################
############# Constants ######################
##############################################

def getAbsPath(index=-1):
    curr_path = sys.path[0]
    paths = curr_path.split('/')[:index]
    abs_path = '/'.join(paths)
    return abs_path


base_path = getAbsPath() + '/AllSource/SourceCode/'
page_size = 10
pop_page_size = 5


##############################################
############# Methods ########################
##############################################

def handleDatas(columnNames, projects):
    datas = []
    for project in projects:
        data = []
        for columnName in columnNames:
            cdata = str(project.__getattribute__(columnName))
            data.append(cdata)
        datas.append([project.id, data])
    return datas

def handleTestDatas(tests):
    datas = []
    columnNames = []
    allColumnNames = []

    pColumnNames = Project.getShowColumns()
    columnNames += pColumnNames
    allColumnNames.append('Project')
    allColumnNames += Project.getColumns()
    sColumnNames = AppBinary.getShowColumns()
    columnNames += sColumnNames
    allColumnNames.append('ApplicationBinary/Dockerfile')
    allColumnNames += AppBinary.getColumns()
    tColumnNames = Test.getShowColumns()
    columnNames += tColumnNames
    allColumnNames.append('Test')
    allColumnNames += Test.getColumns()

    for test in tests:
	project = test.project
	appBinary = test.appBinary
	data = [] 
	for column in pColumnNames:
		cdata = str(project.__getattribute__(column))
		data.append(cdata)
	for column in sColumnNames:
		cdata = str(appBinary.__getattribute__(column))
		data.append(cdata)
	for column in tColumnNames:
		cdata = str(test.__getattribute__(column))
		data.append(cdata)
	datas.append([test.id, data])
    return datas, columnNames, allColumnNames
	

def handle_new_request(item='tests', starts=[0, 0, 0, 0, 0], pop=False):
    if pop:
        size = pop_page_size
    else:
        size = page_size

    if item == 'tests':
        s = starts[0]
        e = s + size
        rawDatas = Test.objects.order_by('-id')[s:e]
	datas, columnNames, allColumnNames = handleTestDatas(rawDatas)
    elif item == 'results':
        s = starts[1]
        e = s + size
        rawDatas = Result.objects.order_by('-id')[s:e]
        columnNames = Result.getShowColumns()
	allColumnNames = Result.getColumns()
    	datas = handleDatas(columnNames, rawDatas)
    elif item == 'machines':
	s = starts[2]
	e = s + size
	rawDatas = MachineModel.objects.order_by('-id')[s:e]
	columnNames = MachineModel.getColumns()
	allColumnNames = []
	datas = handleDatas(columnNames, rawDatas)
    elif item == 'projects':
	s = starts[3]
	e = s + size
	rawDatas = Project.objects.order_by('-id')[s:e]
	columnNames = Project.getColumns()
	allColumnNames = []
	datas = handleDatas(columnNames, rawDatas)
    elif item == 'source codes':
	s = starts[4]
	e = s + size
	rawDatas = AppBinary.objects.order_by('-id')[s:e]
	columnNames = AppBinary.getColumns()
	allColumnNames = []
	datas = handleDatas(columnNames, rawDatas)

    cleanNames = []
    for name in columnNames:
        cleanNames.append(name.replace('_', ' '))

    allCleanNames = []
    for name in allColumnNames:
	allCleanNames.append(name.replace('_', ' '))

    excludeColumns = ['target', 'project', 'appBinary', 'pid']
    foreignColumns = ['machine',]
    uploadColumns = ['source path', ]
    textAreaInputs = ['description', ]
    headColumns = ['Project', 'ApplicationBinary/Dockerfile', 'Test']
    columnsInfo = []
    for column in allCleanNames:
	lineType = 'normal'
	inputType = 'normal'
	buttonType = 'normal'

	if column in excludeColumns:
	    continue

	if column in headColumns:
	    lineType = 'headline'
	    inputType = 'none'
	    if not column == 'Test':
	    	buttonType = 'headchoose'
        elif column in foreignColumns:
            inputType = 'disable'
	    buttonType = 'choose'
        elif column in uploadColumns:
	    inputType = 'disableupload'
	    buttonType = 'upload'
	elif column in textAreaInputs:
	    inputType = 'textarea'
	columnsInfo.append((column, lineType, inputType, buttonType))

    context = {
        's': s + 1,
        'e': e,
        'tps': starts[0],
        'rps': starts[1],
	'mps': starts[2],
	'pps': starts[3],
	'sps': starts[4],
        'itemName': item,
	'columnNames': cleanNames,
        'columnsInfo': columnsInfo,
        'datas': datas,
        }
    return context

def handle_upload_files(sPath, files):
    if not os.path.isdir(base_path):
        os.makedirs(base_path)
    tmp = base_path
    tmpPaths = sPath.split('/')
    paths = []
    for path in tmpPaths:
	if path: paths.append(path)
    for path in paths:
        tmp = tmp + '/' + path
        tmps = tmp.split(' ')
        tmp = ''.join(tmps)
        if not os.path.isdir(tmp):
            os.mkdir(tmp)
    for file in files:
        with open(os.path.join(tmp, file.name), 'w') as ofile:
            for chunk in file.chunks():
                ofile.write(chunk)


def handle_file_delete(sPath):
    tmpPaths = sPath.split('/')
    paths = []
    for path in tmpPaths:
	if path: paths.append(path)
    clean_paths = []
    for path in paths:
        tmps = str(path).split(' ')
        clean_paths.append(''.join(tmps))
    tmp = base_path + '/' + '/'.join(clean_paths)
    try:
        shutil.rmtree(tmp)
        i = 3
        while i > 0:
            tmp = base_path + '/' + '/'.join(clean_paths[:i])
            if not os.listdir(tmp):
                shutil.rmtree(tmp)
            else:
                break
            i = i - 1
    except OSError:
        pass

def createPath(basePath, rPaths):
	paths = rPaths.split('/')
	tmp = basePath
	for path in paths:
		tmp += '/' + path
		if not os.path.isdir(tmp): os.mkdir(tmp)

def copyPath(basePath, srcPath, desBasePath):
	if basePath == desBasePath: return False
	tmpsrc = basePath + '/' + srcPath
	createPath(desBasePath, srcPath)
	tmpdes = desBasePath + '/' + srcPath
	files = os.listdir(tmpsrc)
	for file in files:
		if os.path.isdir(tmpsrc+'/'+file):
			copyPath(basePath, srcPath+'/'+file, desBasePath)
			continue
		shutil.copy(basePath+'/'+srcPath+'/'+file, tmpdes+'/'+file)
	return True

def deletePath(basePath, rPath):
	rawPaths = rPath.split('/')
	paths = []
	for path in rawPaths:
		if path: paths.append(path)
	shutil.rmtree(basePath+'/'+rPath)
	count = len(paths) - 1
	while count > 0:
		tmp = basePath+'/'+'/'.join(paths[:count])
		if os.listdir(tmp): break
		shutil.rmtree(tmp)
		count -= 1
	

