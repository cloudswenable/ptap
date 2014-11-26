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

from showControler.models import *
from function_views import *

##############################################
############# Views ##########################
##############################################

class ShowView(View):

    def get(
        self,
        request,
        *args,
        **kwargs
        ):
        type = request.GET['type']
        if type == 'results':
            id = request.GET['id']
            id = int(id)
            if id:
                result = Result.objects.get(pk=id)
                status = result.status
                if not status == 'done':
                    data = {'categories': [],
                            'series': [{'name': result.result_name,
                            'data': []}]}
                else:
		    rPath = result.result_path
		    results = frontendAgent.queryAResultOverview([rPath])
                    cateNames = [item[0] for item in results]
                    datas = [item[1] for item in results]
                    data = {'categories': cateNames,
                            'series': [{'name': result.result_name,
                            'data': datas}]}
                return HttpResponse(json.dumps(data),
                                    content_type='text/json')

class StopView(View):
        def get(self, request, *args, **kwargs):
                id = request.GET['id']
                result = Result.objects.get(pk=id)
                fileno = result.test.machine.fileno
                frontendAgent.enqueue((6, [id, fileno]))
                return HttpResponseRedirect(reverse('showControler:redirectnew', args=('results',)))

class RunView(View):
    def get(self, request, *args, **kwargs):
        id = request.GET['id']
        if id:
            id = int(id)
            test = Test.objects.get(pk=id)
            old_results = test.result_set.all()
            #for old_result in old_results:
             #   old_result.delete()

            curr_date = timezone.now()
            rName = test.test_name + ' result'
            rPath = test.getBasePath(curr_date)
	    target = test.target
	    sourcePath = ''
	    pid = -1
	    sourcePath = test.appBinary.getPath()
	    appBinaryId = test.appBinary.id
            result = Result(result_name=rName, test=test, test_date=curr_date, result_path=rPath, status='undone')
            result.save()
	    resultId = result.id
	    machine = test.machine
	    ip = machine.ip
	    fileno = machine.fileno
	    duration = test.duration
	    #repeat = test.repeat
            repeat = 1
	    delaytime = test.delaytime
	    if machine.active:
		frontendAgent.enqueue((1, [rPath,target,duration,repeat,delaytime,appBinaryId,ip,sourcePath,pid,resultId,fileno]))

	    return HttpResponseRedirect(reverse('showControler:redirectnew', args=('results',)))


class NewView(View):

    steps = ['tests', 'results']

    def get(
        self,
        request,
        *args,
        **kwargs
        ):
        chooseItem = kwargs.get('chooseItem')
        if not chooseItem:
            chooseItem = self.steps[0]
        context = {
            'new': True,
            'chooseItem': chooseItem,
            'dirItems': self.steps,
            }
        anoContext = handle_new_request(item=chooseItem, starts=[0, 0, 0, 0, 0])
        context = dict(context.items() + anoContext.items())
        return render(request, 'showControler/pages/new_content.html',
                      context)


class ShowTableView(View):

    results_table_name = 'showControler/pages/resultsContentTable.html'
    new_table_name = 'showControler/pages/new_right_content.html'

    def get(
        self,
        request,
        *args,
        **kwargs
        ):
        type = request.GET.get('type')
        item = request.GET.get('item')
        pps = request.GET.get('pps')
        if not pps:
            pps = 0
        else:
            pps = int(pps)
        mps = request.GET.get('mps')
        if not mps:
            mps = 0
        else:
            mps = int(mps)
        sps = request.GET.get('sps')
        if not sps:
            sps = 0
        else:
            sps = int(sps)
        tps = request.GET.get('tps')
        if not tps:
            tps = 0
        else:
            tps = int(tps)
        rps = request.GET.get('rps')
        if not rps:
            rps = 0
        else:
            rps = int(rps)

        if type == 'new':
            context = handle_new_request(item, starts=[tps, rps, mps, pps, sps])
            return render(request, self.new_table_name, context)
        else:
            raise Http404


class AddModelsView(View):

    def post(
        self,
        request,
        *args,
        **kwargs
        ):
        item = request.POST['item']
        if item == 'tests':
	    project_name = request.POST['project name']
	    team_name = request.POST['team name']
	    try:
	    	project = Project.objects.get(project_name=project_name, team_name=team_name)
	    except:
		project = None
	    if project:
		project_id = project.id
	    else:
		project = Project(project_name=project_name, team_name=team_name)
		project.save()
		project_id = project.id

	    binary_name = request.POST['binary name']
	    source_path = request.POST['source path']
	    version = request.POST['version']
	    try:
		appBinary = AppBinary.objects.get(binary_name=binary_name, source_path=source_path, version=version)
	    except:
		appBinary = None
	    changed = False
	    oldPath = ''
	    if appBinary:
		oldPath = appBinary.getPath()
		changed = True
		appBinary.project = project
		appBinary.save()
		appBinary_id = appBinary.id
	    else:
		appBinary = AppBinary(binary_name=binary_name, project=project, source_path=source_path, version=version)
		appBinary.save()
		appBinary_id = appBinary.id
            print source_path
            print appBinary.getPath()

	    files = request.FILES.getlist('upload')
	    handle_upload_files(appBinary.getPath(), files)
	    if changed:
		ifDelete = copyPath(base_path+'/'+oldPath, '.', base_path+'/'+appBinary.getPath())
		if ifDelete:
			deletePath(base_path, oldPath)

	    test_name = request.POST['test name']
	    machine_id = request.POST['machine']
	    #repeat = request.POST['repeat']
	    repeat = 1
	    duration = request.POST['duration']
	    delaytime = request.POST['delaytime']
	    description = request.POST['description']
	    try:
		machine = MachineModel.objects.get(pk=int(machine_id))
	    except:
		machine = None
	    
	    test = Test(test_name=test_name,project=project,target='platform',appBinary=appBinary,pid=-1,machine=machine,repeat=repeat,duration=duration,delaytime=delaytime,description=description)
	    test.save()
	    return HttpResponseRedirect(reverse('showControler:redirectnew', args=(item, )))
	
        else:
            raise Http404

class CloneModelsView(View):
    def post(
            self,
            request,
            *args,
            **kwargs
    ):
        item = request.POST['item']

        if item == 'tests':
            project_name = request.POST['project name']
            team_name = request.POST['team name']
            try:
                project = Project.objects.get(project_name=project_name, team_name=team_name)
            except:
                project = None
            if not project:
                project = Project(project_name=project_name, team_name=team_name)
                project.save()

            binary_name = request.POST['binary name']
            source_path = request.POST['source path']
            version = request.POST['version']
            try:
                appBinary = AppBianry.objects.get(binary_name=binary_name, source_path=source_path,
                                                    version=version)
            except:
                appBinary = None
            changed = False
            oldPath = ''
            if appBinary:
                oldPath = appBinary.getPath()
                appBinary.project = project
                appBinary.save()
                changed = True
            else:
                appBinary = AppBinary(binary_name=binary_name, project=project, source_path=source_path,
                                        version=version)
                appBinary.save()
            files = request.FILES.getlist('upload')
            handle_upload_files(appBinary.getPath(), files)
            if changed:
                ifDelete = copyPath(base_path + '/' + oldPath, '.', base_path + '/' + appBinary.getPath())
                if ifDelete: deletePath(base_path, oldPath)

            test_name = request.POST['test name']
            machine_id = request.POST['machine']
            repeat = 1
            duration = request.POST['duration']
            delaytime = request.POST['delaytime']
            description = request.POST['description']

            try:
                machine = MachineModel.objects.get(pk=int(machine_id))
            except:
                machine = None

            test = Test(test_name=test_name, project=project, target='platform', appBinary=appBinary, pid=-1,
                        machine=machine, repeat=repeat, duration=duration, delaytime=delaytime, description=description)
            test.save()
            return HttpResponseRedirect(reverse('showControler:redirectnew', args=(item, )))

        else:
            raise Http404


class LoadTestDatasView(View):
    def get(self, request, *args, **kwargs):
	testId = int(request.GET['testId'])
	data = {}
	if testId:
		test = Test.objects.get(pk=testId)
		project = test.project
		appBinary = test.appBinary
		machine = test.machine
		data['project name'] = project.project_name
		data['team name'] = project.team_name
		data['source code name'] = appBinary.binary_name
		data['source path'] = 'source'
		data['version'] = appBinary.version
		data['test name'] = test.test_name
		data['machine'] = (machine.id, machine.name)
		data['repeat'] = test.repeat
		data['duration'] = test.duration
		data['delaytime'] = test.delaytime
		data['description'] = test.description
	return HttpResponse(json.dumps(data), content_type='text/json')

from django.db import connection
class LoadCloneDatasView(View):
    def get(self, request, *args, **kwargs):
	testId = int(request.GET['testId'])
	data = {}
	if testId:
		test = Test.objects.get(pk=testId)
		project = test.project
		appBinary = test.appBinary
		machine = test.machine
		data['project name'] = project.project_name
		data['team name'] = project.team_name
		data['binary name'] = appBinary.binary_name
		data['source path'] = 'source'
		data['version'] = appBinary.version
		data['test name'] = test.test_name
		data['machine'] = (machine.id, machine.name)
		data['repeat'] = test.repeat
		data['duration'] = test.duration
		data['delaytime'] = test.delaytime
		data['description'] = test.description
        cursor = connection.cursor()

        sqlcmd = "select max(version) from showControler_appbinary where binary_name='" + appBinary.binary_name + \
                 "' and project_id="+ str(appBinary.project_id) + " and source_path='" + appBinary.source_path + "'"
        cursor.execute(sqlcmd)
        data['version'] = cursor.fetchone()[0]

	return HttpResponse(json.dumps(data), content_type='text/json')

class ModifyModelsView(View):

    def post(
        self,
        request,
        *args,
        **kwargs
        ):
        item = request.POST['item']
	
        if item == 'tests':
	    project_name = request.POST['project name']
	    team_name = request.POST['team name']
	    try:
		project = Project.objects.get(project_name=project_name,team_name=team_name)
	    except:
		project = None
	    if not project:
		project = Project(project_name=project_name,team_name=team_name)
		project.save()

	    binary_name = request.POST['binary name']
	    source_path = request.POST['source path']
	    version = request.POST['version']
	    try:
		appBinary = AppBinary.objects.get(binary_name=binary_name, source_path=source_path, version=version)
	    except:
		appBinary = None
	    changed = False
	    oldPath = ''
	    if appBinary:
		oldPath = appBinary.getPath()
		appBinary.project = project
		appBinary.save()
		changed = True	
	    else:
		appBinary = AppBinary(binary_name=binary_name, project=project, source_path=source_path, version=version)
		appBinary.save()
	    files = request.FILES.getlist('upload')
            handle_upload_files(appBinary.getPath(), files)
	    if changed:
		ifDelete = copyPath(base_path+'/'+oldPath, '.', base_path+'/'+appBinary.getPath())
		if ifDelete: deletePath(base_path, oldPath)
	
            testId = int(request.POST['id'])
	    test_name = request.POST['test name']
	    machine_id = request.POST['machine']
	    #repeat = request.POST['repeat']
	    duration = request.POST['duration']
	    delaytime = request.POST['delaytime']
	    description = request.POST['description']
	    
	    try:
		machine = MachineModel.objects.get(pk=int(machine_id))
	    except:
		machine = None

            test = Test.objects.get(pk=testId)
            if test:
                test.test_name = test_name
		test.project = project
		test.appBinary = appBinary
		test.machine = machine
		#test.repeat = repeat
		test.duration = duration
		test.delaytime = delaytime
		test.description = description
		test.save()
            return HttpResponseRedirect(reverse('showControler:redirectnew'
                    , args=(item, )))
        else:
            raise Http404


class PopContentView(View):

    pop_content_table = 'showControler/pages/new_choose_pop_table.html'

    def get(
        self,
        request,
        *args,
        **kwargs
        ):
        item = request.GET['item']
        tps = int(request.GET['tps'])
	mps = int(request.GET['mps'])
	pps = int(request.GET['pps'])
	sps = int(request.GET['sps'])
        context = handle_new_request(item, starts=[tps,0, mps, pps, sps], pop=True)
        return render(request, self.pop_content_table, context)


class DeleteModelsView(View):

    def deleteResult(self, result):
        rPath = result.result_path
	frontendAgent.enqueue((2, [rPath,'AllSource/ServerOutput']))
	result.delete()
    
    def deleteTest(self, test):
	    project = test.project
	    appBinary = test.appBinary

            tmpTestSet = appBinary.test_set.all()
	    testWantDeleteAppBinary = False
	    if len(tmpTestSet) <= 1:# current test
		    testWantDeleteAppBinary = True

	    testWantDeleteProject = False
	    tmpTestSet2 = project.test_set.all()
	    if len(tmpTestSet2) <= 1: # only current test
		    testWantDeleteProject = True
		
	    appBinaryWantDeleteProject = False
	    tmpAppBinarySet = project.appbinary_set.all()
	    if len(tmpAppBinarySet) <= 1 and testWantDeleteAppBinary: # only current source code
		    appBinaryWantDeleteProject = True

            test.delete()
	    if testWantDeleteAppBinary:
		    handle_file_delete(appBinary.getPath())
		    appBinary.delete()
	    if testWantDeleteProject and appBinaryWantDeleteProject:
		    project.delete()

    def get(
        self,
        request,
        *args,
        **kwargs
        ):
        item = request.GET['item']
        id = request.GET['id']
        if not id or id == 'undefined':
            return HttpResponseRedirect(reverse('showControler:redirectnew'
                    , args=(item, )))

        if item == 'tests':
            test = Test.objects.get(pk=id)
            results = test.result_set.all()
            if not results:
                self.deleteTest(test)
            else:
                #detete results first
                for result in results:
                    self.deleteResult(result)
                self.deleteTest(test)
	elif item == 'results':
	    r = Result.objects.get(pk=id)
            self.deleteResult(r)
        else:
            raise Http404
        return HttpResponseRedirect(reverse('showControler:redirectnew'
                                    , args=(item, )))


