#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.http import Http404
from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse
from django.views import generic
from django import forms
from django.views.generic import View
from django.utils import timezone

import sys
import os
import re
import shutil
import json
import random

tmp_path = sys.path[0]
if not tmp_path in sys.path:
    sys.path.append(tmp_path)

from showControler.models import *
from function_views import *

##############################################
############# Views ##########################
##############################################
servicePageSize = 10
def getServices(chooseItem, start=0, end=10):
        columnNames = []
        datas = []
        if chooseItem == 'services':
                services = Service.objects.order_by('-id')[start:end]
                columnNames = Service.getShowColumns()
                datas = []
                for service in services:
                        data = []
                        for columnName in columnNames:
                                data.append(service.__getattribute__(columnName))
                        datas.append([service.id, data])
        elif chooseItem == 'results':
                results = ServiceResult.objects.order_by('-id')[start:end]
                columnNames = ServiceResult.getShowColumns()
                datas = []
                for result in results:
                        data = []
                        for column in columnNames:
                                data.append(str(result.__getattribute__(column)))
                        datas.append([result.id, data])
        elif chooseItem == 'analysises':
                analysises = ServiceAnalysis.objects.order_by('-id')[start:end]
                columnNames = ServiceAnalysis.getShowColumns()
                datas = []
                for analysis in analysises:
                        data = []
                        for column in columnNames:
                                data.append(str(analysis.__getattribute__(column)))
                        datas.append([analysis.id, data])
        cleanColumnNames = []
        for column in columnNames:
                cleanColumnNames.append(column.replace('_', ' '))
        return cleanColumnNames, datas

def getServiceColumnsInfo(chooseItem):
        columnsInfo = []
        columnNames = []
        if chooseItem == 'services':
                columnNames = Service.getColumns()
        elif chooseItem == 'results':
                columnNames = ServiceAnalysis.getColumns()

        firstColumns = ['service_name', 'analysis_name',]
        foreignColumns = ['service_machine',]
        foreignColumnsWithoutButton = ['service_result',]
        selectColumns = ['type', ]
        textAreaInputs = ['service_description', 'analysis_description',]
        for column in columnNames:
                lineType = 'normal'
                inputType = 'normal'
                buttonType = 'normal'

                if column in firstColumns:
                        lineType = 'firstline'
                if column in foreignColumns:
                        inputType = 'disable'
                        buttonType = 'choose'
                if column in foreignColumnsWithoutButton:
                        inputType = 'disable'
                        buttonType = 'hiddenInput'
                if column in selectColumns:
                        inputType = 'select'
                if column in textAreaInputs:
                        inputType = 'textarea'
                columnsInfo.append((column.replace('_', ' '), lineType, inputType, buttonType))
        return columnsInfo

class ServiceRightContentView(View):
        service_right_content_page = 'showControler/pages/service_right_content.html'
        def get(self, request, *args, **kwargs):
                start = int(request.GET['start'])
                end = start + servicePageSize
                chooseItem = request.GET['chooseItem']
                if not chooseItem:
                        chooseItem = 'services'
                columnNames, datas = getServices(chooseItem, start, end)
                columnsInfo = getServiceColumnsInfo(chooseItem)
                context = {'columnsInfo':columnsInfo, 'columnNames':columnNames, 'datas': datas, 'itemName': chooseItem, 's': start+1, 'e': end, 'start': start}
                return render(request, self.service_right_content_page, context)

class ServiceView(View):

        service_content_page = 'showControler/pages/service_content.html'
        steps = ['services', 'results', 'analysises']

        def get(self, request, *args, **kwargs):
                items = self.steps
                chooseItem = kwargs.get('chooseItem')
                if not chooseItem:
                        chooseItem = self.steps[0]
                itemName = chooseItem
                s = 1
                e = 10
                columnNames, datas = getServices(chooseItem, s-1, e)
                columnsInfo = getServiceColumnsInfo(chooseItem)
                context = {'columnsInfo':columnsInfo, 'columnNames':columnNames, 'datas': datas, 'chooseItem': chooseItem, 'dirItems': items, 'service':True, 'itemName': itemName, 's': s, 'e': e, 'start': 0}
                return render(request, 'showControler/pages/service_content.html', context)

class AddOrModifyServiceView(View):
        def get(self, request, *args, **kwargs):
                menuType = request.GET['menuType']
                if menuType == 'services':
                        modify = int(request.GET['modify'])
                        serviceName = request.GET['service name']
                        serviceMachineID = int(request.GET['service machine'])
                        totalDuration = int(request.GET['total duration'])
                        duration = int(request.GET['duration'])
                        interval = int(request.GET['interval'])
                        serviceDescription = request.GET['service description']
                        if not modify:
                                machine = MachineModel.objects.get(pk=serviceMachineID)
                                service = Service(service_name=serviceName, service_machine=machine, total_duration=totalDuration, duration=duration, interval=interval, service_description=serviceDescription)
                                service.save()
                        else:
                                machine = MachineModel.objects.get(pk=serviceMachineID)
                                serviceID = int(request.GET['id'])
                                service = Service.objects.get(pk=serviceID)
                                service.service_name = serviceName
                                service.service_machine = machine
                                service.total_duration = totalDuration
                                service.duration = duration
                                service.interval = interval
                                service.service_description = serviceDescription
                                service.save()
                        return HttpResponseRedirect(reverse('showControler:redirectservice', args=('services',)))
                elif menuType == 'results':
                        analysisName = request.GET['analysis name']
                        serviceResultId = int(request.GET['service result'])
                        serviceResult = ServiceResult.objects.get(pk=serviceResultId)
                        featuresCount = int(request.GET['features count'])
                        type = request.GET['type']
                        analysisDescription = request.GET['analysis description']
                        serviceAnalysis = ServiceAnalysis(analysis_name=analysisName,service_result=serviceResult, features_count=featuresCount, type=type, status='undone', analysis_description=analysisDescription)
                        serviceAnalysis.save() 
                        return HttpResponseRedirect(reverse('showControler:redirectservice', args=('analysises',)))

class LoadServiceDatasView(View):

        def get(self, request, *args, **kwargs):
                id = int(request.GET['id'])
                data = {}
                if id:
                        service = Service.objects.get(pk=id)
                        data['service name'] = service.service_name
                        data['service machine'] = (service.service_machine.id, service.service_machine.name)
                        data['total duration'] = service.total_duration
                        data['duration'] = service.duration
                        data['interval'] = service.interval
                        data['service description'] = service.service_description
                return HttpResponse(json.dumps(data), content_type='text/json')

class DeleteServiceView(View):
        def get(self, request, *args, **kwargs):
                id = int(request.GET['id'])
                chooseItem = request.GET['chooseItem']
                if chooseItem == 'services':
                        service = Service.objects.get(pk=id)
                        serviceResults = service.serviceresult_set.all()
                        if not serviceResults:
                                service.delete()
                elif chooseItem == 'results':
                        result = ServiceResult.objects.get(pk=id)
                        if result:
                                serviceAnalysises = result.serviceanalysis_set.all()
                                if not serviceAnalysises:
                                        result.delete()
                                        rPath = result.getPath()
                                        frontendAgent.enqueue((2, [rPath,'ServerOutputService']))
                elif chooseItem == 'analysises':
                        analysis = ServiceAnalysis.objects.get(pk=id)
                        if analysis:
                                rPath = analysis.getPath()
                                frontendAgent.enqueue((2, [rPath,'ServerOutputService']))
                                analysis.delete()
                return HttpResponseRedirect(reverse('showControler:redirectservice', args=(chooseItem,)))

class ServiceRunView(View):
        def get(self, request, *args, **kwargs):
                id = int(request.GET['id'])
                service = Service.objects.get(pk=id)
                serviceResults = service.serviceresult_set.all()
                for result in serviceResults:
                        rPath = result.getPath()
                        frontendAgent.enqueue((2, [rPath,'ServerOutputService']))
                        result.delete()
                name = service.service_name + " result"
                date = timezone.now()
                status = "undone"
                result = ServiceResult(service_result_name=name, result_date=date, service=service, status=status)
                result.save()
                
                machine = service.service_machine
                if machine.active:
                        rPath = result.getPath()
                        switchFileno = machine.fileno
                        totalDuration = service.total_duration
                        duration = service.duration
                        interval = service.interval
                        resultId = result.id
                        parameters = [rPath, switchFileno, totalDuration, duration, interval, resultId] 
                        frontendAgent.enqueue((4, parameters))
        
                return HttpResponseRedirect(reverse('showControler:redirectservice', args=('results',)))

class ServiceAnalysisView(View):
        def get(self, request, *args, **kwargs):
                id = int(request.GET['id'])
                analysis = ServiceAnalysis.objects.get(pk=id)
                result = analysis.service_result
                if result.status == 'done':
                        inputRPath = result.getPath()
                        outputRPath = analysis.getPath()
                        type = analysis.type
                        featuresCount = analysis.features_count
                        parameters = [inputRPath, outputRPath, type, featuresCount, analysis.id]
                        frontendAgent.enqueue((5, parameters))
                        analysis.status = 'undone'
                        analysis.save()
                return HttpResponseRedirect(reverse('showControler:redirectservice', args=('analysises',)))
        
class ServiceShowView(View):
        service_show_blank_page = 'showControler/pages/service_show_blank_page.html'
        def get(self, request, *args, **kwargs):
                id = int(request.GET['id'])
                analysis = ServiceAnalysis.objects.get(pk=id)
                context = {}
                if analysis.status == 'done':
                        rPath = analysis.getPath()
                        context = frontendAgent.queryServiceResults([rPath])
                context['analysisName'] = analysis.analysis_name
                return render(request, self.service_show_blank_page, context)
