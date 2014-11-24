#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

from showControler import views
from showControler.views import *

urlpatterns = patterns(
    '',
    url(r'^$', AnalysisView.as_view(), name='index'),
    url(r'^analysiscontent$', AnalysisRightContentView.as_view(),
        name='analysiscontent'),
    url(r'^analysiscompare$', AnalysisCompareView.as_view(), name='analysiscompare'),
    url(r'^analysismodelsanalysis$', AnalysisModelsAnalysisView.as_view(), name='analysismodelsanalysis'),
    url(r'^analysisoverview$', AnalysisOverviewView.as_view(), name='analysisoverview'),
    url(r'^analysisdynamicoverview$', AnalysisDynamicOverviewView.as_view(), name='analysisdynamicoverview'),
    url(r'^analysisanalysis$', AnalysisAnalysisView.as_view(), name='analysisanalysis'),
    url(r'^analysisanalysisrightpage$', AnalysisAnalysisRightPageView.as_view(), name='analysisanalysisrightpage'),
    url(r'^loadcomparetable$', LoadCompareTableView.as_view(), name='loadcomparetable'),
    url(r'^loaddynamicdatas$', LoadDynamicDatasView.as_view(), name='loaddynamicdatas'),

    url(r'^new/$', NewView.as_view(), name='new'),
    url(r'^new/(?P<chooseItem>.+)$', NewView.as_view(),name='redirectnew'),
    url(r'^showtable/$', ShowTableView.as_view(), name='showtable'),
    url(r'^add/$', AddModelsView.as_view(), name='add'),
    url(r'^delete/$', DeleteModelsView.as_view(), name='delete'),
    url(r'^clone/$', CloneModelsView.as_view(), name='clone'),
    url(r'^loadtestdatas/$', LoadTestDatasView.as_view(), name='loadtestdatas'),
    url(r'^modify/$', ModifyModelsView.as_view(), name='modify'),
    url(r'^getpoptable/$', PopContentView.as_view(), name='getpoptable'),
    url(r'^run/$', RunView.as_view(), name='run'),
    url(r'^stop/$', StopView.as_view(), name='stop'),
    url(r'^showresult/$', ShowView.as_view(), name='showresult'),

    url(r'^system/$', SystemShowView.as_view(), name='system'),
    url(r'^sync/$', SyncMachinesView.as_view(), name='sync'),
    url(r'^clear/$', ClearMachinesView.as_view(), name='clear'),

    url(r'^service/$', ServiceView.as_view(), name='service'),
    url(r'^service/(?P<chooseItem>.+)$', ServiceView.as_view(),name='redirectservice'),
    url(r'^addormodifyservice/$', AddOrModifyServiceView.as_view(), name='addormodifyservice'),
    url(r'^loadservicedatas/$', LoadServiceDatasView.as_view(), name='loadservicedatas'),
    url(r'^deleteservice/$', DeleteServiceView.as_view(), name='deleteservice'),
    url(r'^servicerightcontent/$', ServiceRightContentView.as_view(), name='servicerightcontent'),
    url(r'^servicerun/$', ServiceRunView.as_view(), name='servicerun'),
    url(r'^serviceanalysis/$', ServiceAnalysisView.as_view(), name='serviceanalysis'),
    url(r'^serviceshow/$', ServiceShowView.as_view(), name='serviceshow'),
    )
