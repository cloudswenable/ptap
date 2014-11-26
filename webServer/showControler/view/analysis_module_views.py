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

class AnalysisView(View):

    analysis_content_page = 'showControler/pages/analysis_content.html'

    def get(
        self,
        request,
        *args,
        **kwargs
        ):
        projects = Project.objects.order_by('-id')
        items = []
        for project in projects:
            items.append((project.id, project.project_name))
	chooseItem = ''
	if items: chooseItem = items[0][1]
        return render(request, self.analysis_content_page, {
            'analysis': True,
            'title': 'Projects: ',
            'chooseItem': chooseItem,
            'dirItems': items,
            })


class AnalysisRightContentView(View):

    def get(
        self,
        request,
        *args,
        **kwargs
        ):
        id = request.GET['id']
        project = Project.objects.get(pk=int(id))
	projectInfo = project.getInfo()
        sourcecodes = project.appbinary_set.all()
	allResults = []
	alltests = project.test_set.order_by('-id')
	for test in alltests:
	    testInfo = test.getInfo()
	    appBinary= test.appBinary
	    sourcecodeInfo = []
	    if appBinary:
		sourcecodeInfo = appBinary.getInfo()
	    machineInfo = test.machine.getInfo()
	    results = test.result_set.all()
	    for result in results:
		resultInfo = result.getInfo()
		resultItem = {'name': result.result_name, 'id': result.id}
		attrs = resultInfo + testInfo + machineInfo + sourcecodeInfo + projectInfo
		resultItem['attrs'] = attrs
		allResults.append(resultItem)
	
        return HttpResponse(json.dumps(allResults),
                            content_type='text/json')

class AnalysisCompareView(View):
    analysis_compare_blank_page = 'showControler/pages/analysis_compare_blank_page.html'
    tableSize = 10

    def get(
        self,
        request,
        *args,
        **kwargs
        ):
        ids = request.GET.getlist('ids')
        resultsPaths = []
	resultsNames = ['']
        for id in ids:
	    result = Result.objects.get(pk=int(id))
            if not (result.status == 'done'): continue
            resultsPaths.append(result.result_path)
	    resultsNames.append(result.result_name)
        if resultsPaths:
	    results = frontendAgent.queryResults([resultsPaths, ['pmu metrics', 'pmu events', 'perf list metrics', 'perf list events', 'hotspots', 'sar metrics'], [(0, self.tableSize), (0, self.tableSize), (0, self.tableSize), (0, self.tableSize), (0, self.tableSize), (0, self.tableSize)]])
	    context = {'names': resultsNames, 'datas': results, 'ids': ids, 'start':1, 'end':self.tableSize}
        else:
	    context = []
        return render(request, self.analysis_compare_blank_page, context)

class AnalysisModelsAnalysisView(View):
        analysis_modelsAnalysis_blank_page = 'showControler/pages/analysis_modelsAnalysis_blank_page.html'
        def get(self, request, *args, **kwargs):
                id = request.GET.getlist('ids')[0]
                rPath = None
                if id:
                        result = Result.objects.get(pk=int(id))
                        if result.status == 'done':
                                rPath = result.result_path
                if rPath:
                        rawResults = frontendAgent.queryModelsResults([rPath])
                cpus = []
                mems = []
                ios = []
                nets = []
                powers = []
                chooseModel = 'None Model'
                summary = 'None'
                metrics = []
                if rawResults:
                        cpus, mems, ios, nets, powers, chooseModel, summary, metrics = rawResults
                context = {'cpus': cpus, 'mems': mems, 'ios': ios, 'nets': nets, 'powers':powers, 'chooseModel':chooseModel, 'summary': summary, 'metrics': metrics}
                return render(request, self.analysis_modelsAnalysis_blank_page, context)

class AnalysisDynamicOverviewView(View):
        analysis_dynamic_overview_blank_page = 'showControler/pages/analysis_dynamic_overview_blank_page.html'
        def get(self, request, *args, **kwargs):
                ids = request.GET.getlist('ids')
                context = {'id':ids[0]}
                return render(request, self.analysis_dynamic_overview_blank_page, context)

class LoadDynamicDatasView(View):
        def get(self, request, *args, **kwargs):
                id = request.GET['id']
                qtables = request.GET.getlist('qtables')
                starts = request.GET.getlist('starts')
                next = request.GET['next']
                allResults = []
                if id:
                        result = Result.objects.get(pk=int(id))
                        rPath = result.result_path
                        allResults = frontendAgent.queryDynamicOverviews([rPath, qtables, starts, next]);
                        
                #allResults = [['perf', ['a', 'b', 'c'], [1,2,3], [[1,2,3,4,5],[2,0,4, 10, 11],[5,6,7,2,1]], ['1s', '2s', '3s', '4s', '5s']], ['pmu', ['a', 'b', 'c'], [3,4,5], [[1,2,3,4,5],[2,3,4,3,2],[3,4,5,0,1]], ['1s', '2s', '3s', '4s', '5s']]]
                return HttpResponse(json.dumps(allResults),content_type='text/json')
                

class AnalysisOverviewView(View):
        analysis_overview_blank_page = 'showControler/pages/analysis_overview_blank_page.html'
        
        def get(self, request, *args, **kwargs):
                ids = request.GET.getlist('ids')
                resultsPaths = []
                resultsNames = ['']
                for id in ids:
                        result = Result.objects.get(pk=int(id))
                        if not (result.status == 'done'): continue
                        resultsPaths.append(result.result_path)
                        resultsNames.append(result.result_name)
                if resultsPaths:
                        rawResults = frontendAgent.queryOverviews([resultsPaths])
                        results = []
                        for rawResult in rawResults:
                                tmp = [rawResult[0], rawResult[0].replace(' ', ''), rawResult[1]]
                                results.append(tmp)
                        context = {'names':resultsNames, 'datas': results,}
                else:
                        context = {}
                return render(request, self.analysis_overview_blank_page, context)

class AnalysisAnalysisView(View):
        analysis_analysis_blank_page = 'showControler/pages/analysis_analysis_blank_page.html'
        titles = [[0, 'groupOne', 'performance data overview', [[0, 'self-defined performance matrix'],[1,'cpu freq'],[2, 'cpu utilization'],[3, 'cpi'],[4, 'path length']]], [1, 'groupTwo', 'per-core analysis', [[0, 'per-core/socket cpu utilization']]], [2, 'groupThree', 'pmu related data analysis', [[0, 'numa locality'], [1, 'cache misses'], [2, 'qpi'], [3, 'memory']]], [3, 'groupFour', 'system data level analysis', [[0, 'interrupt/s'],[1,'cs/s'],[2, 'network io'], [3, 'disk io']]], [4, 'groupFive', 'hotspot analysis',[[0, 'hotspot']]]]

        def get(self, request, *args, **kwargs):
                ids = request.GET.getlist('ids')
                context = {'ids': ids, 'titles': self.titles}
                return render(request, self.analysis_analysis_blank_page, context)

class AnalysisAnalysisRightPageView(View):
        analysis_analysis_blank_right_page = 'showControler/pages/analysis_analysis_blank_right_page.html'
        def get(self, request, *args, **kwargs):
                ids = request.GET.getlist('ids');
                metricName = request.GET['metricName']
                resultsNames = []
                resultsPaths = []
                for id in ids:
                        try:
                                result = Result.objects.get(pk=int(id))
                        except:
                                continue
                        if not (result.status == 'done'): continue
                        resultsNames.append(result.result_name)
                        resultsPaths.append(result.result_path)
                if resultsPaths:
                        rawResults = frontendAgent.queryAnalysis([resultsPaths, metricName])
                tableHeads = ['', metricName, 'reasonable range', 'suggestion']
                datas = []
                summary = ''
                if rawResults:
                        rawDatas = rawResults['datas']
                        summary = rawResults['summary']
                        for i in range(len(resultsNames)):
                                name = resultsNames[i]
                                value = rawDatas[i][0]
                                tmpRange = str(rawDatas[i][1]) + ' - ' + str(rawDatas[i][2])
                                suggestion = rawDatas[i][3]
                                tmp = [name, value, tmpRange, suggestion]
                                datas.append(tmp)
                
                context = {'title': metricName.upper(), 'tableHeads':tableHeads, 'datas': datas, 'summary': summary}
                return render(request, self.analysis_analysis_blank_right_page, context)

class LoadCompareTableView(View):
	def get(self, request, *args, **kwargs):
		name = request.GET['tableName']
		ids = request.GET.getlist('ids');
		start = request.GET['start'];
		end = request.GET['end'];
		resultsPaths = []
		resultsNames = ['']
		for id in ids:
			result = Result.objects.get(pk=int(id))
            		if not (result.status == 'done'): continue
            		resultsPaths.append(result.result_path)
			resultsNames.append(result.result_name)
		if resultsPaths:
                        tmpStart = int(start) - 1
			results = frontendAgent.queryResults([resultsPaths, [name], [(tmpStart, end)]])
			result = {'datas': results, 'names': resultsNames, 'start': start, 'end': end}
		else:
			result = []
		return HttpResponse(json.dumps(result),
                            content_type='text/json')
