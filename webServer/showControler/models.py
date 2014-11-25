#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.db import models


class Project(models.Model):

    project_name = models.CharField(max_length=200)
    team_name = models.CharField(max_length=200)

    @staticmethod
    def getColumns():
        return ['project_name', 'team_name']

    @staticmethod
    def getShowColumns():
	return ['project_name', ]

    def __unicode__(self):
        return self.project_name

    def getInfo(self):
	tmp = [['team name', self.team_name]]
	return tmp


class SourceCode(models.Model):

    source_code_name = models.CharField(max_length=200)
    project = models.ForeignKey(Project)
    source_path = models.CharField(max_length=200)
    version = models.FloatField(default=0)

    @staticmethod
    def getColumns():
        return ['source_code_name', 'project', 'source_path', 'version']

    @staticmethod
    def getShowColumns():
	return ['source_code_name', 'version']

    def __unicode__(self):
        return self.source_code_name

    def getPath(self):
	tmp = ''.join(self.project.project_name.split(' ')) + '/'
	tmp += ''.join(self.source_code_name.split(' ')) + '/'
	tmp += ''.join(self.source_path.split(' ')) + '/'
	tmp += str(self.version) + '/'
        return  tmp

    def getInfo(self):
	tmp = [['source code name', self.source_code_name], ['source code version', self.version]]
	return tmp


class MachineModel(models.Model):

    name = models.CharField(max_length=200)
    active = models.BooleanField(default=True)
    mac = models.CharField(max_length=100)
    ip = models.CharField(max_length=50)
    fileno = models.CharField(max_length=10)
    os_info = models.CharField(max_length=200)
    cpu_info = models.CharField(max_length=200)
    mem_info = models.CharField(max_length=200)
    disk_info = models.CharField(max_length=200)
    ht = models.BooleanField(default=False)
    turbo = models.BooleanField(default=False)

    @staticmethod
    def getColumns():
        return ['name', 'active', 'ip', 'fileno', 'mac', 'os_info', ]

    @staticmethod
    def getShowColumns():
	return ['name', 'active', 'ip', 'fileno', 'mac', 'os_info', ]

    def __unicode__(self):
        return self.name

    def getInfo(self):
	tmp = [['machine name', self.name], ['active', self.active], ['ip', self.ip],  ]
	return tmp


class Test(models.Model):

    test_name = models.CharField(max_length=200)
    project = models.ForeignKey(Project)
    target = models.CharField(max_length=50)
    sourceCode = models.ForeignKey(SourceCode, null=True)
    pid = models.IntegerField(default=-1)
    machine = models.ForeignKey(MachineModel)
    repeat = models.IntegerField(default=1)
    duration = models.IntegerField(default=10)
    delaytime = models.IntegerField(default=3)
    description = models.CharField(max_length=500)

    @staticmethod
    def getColumns():
        return [
            'test_name',
	    'target',
	    'project',
            'sourceCode',
	    'pid',
            'machine',
            'repeat',
            'duration',
            'delaytime',
	    'description',
            ]

    @staticmethod
    def getShowColumns():
	return ['test_name', 'machine','repeat','duration','delaytime','description',]

    def __unicode__(self):
        return self.test_name

    def getBasePath(self):
	tmp = ''
	tmp = tmp + ''.join(self.project.project_name.split(' ')) + '/'
        sc = self.sourceCode
	if sc:
            tmp = tmp + ''.join(sc.source_code_name.split(' ')) + '/'
            tmp = tmp + ''.join(sc.source_path.split(' ')) + '/'
            tmp = tmp + str(sc.version) + '/'
        tmp = tmp + ''.join(self.test_name.split(' ')) + '/'
        return tmp

    def getInfo(self):
	tmp = [['test name', self.test_name], ['duration', self.duration], ['description', self.description]]
	return tmp


class Result(models.Model):

    result_name = models.CharField(max_length=200)
    test = models.ForeignKey(Test)
    test_date = models.DateTimeField()
    result_path = models.CharField(max_length=300)
    status = models.CharField(max_length=50)

    @staticmethod
    def getColumns():
        return ['result_name', 'test', 'test_date', 'status']

    @staticmethod
    def getShowColumns():
	return ['result_name', 'test', 'test_date', 'status']

    def __unicode__(self):
        return self.result_name

    def getInfo(self):
	tmp = [['test date', str(self.test_date)], ['status', self.status]]
	return tmp

class Service(models.Model):
        service_name = models.CharField(max_length=200)
        service_machine = models.ForeignKey(MachineModel)
        total_duration = models.IntegerField(default=60)
        duration = models.IntegerField(default=10)
        interval = models.IntegerField(default=5)
        service_description = models.CharField(max_length=500)
        
        def __unicode__(self):
                return self.service_name

        @staticmethod
        def getColumns():
                return ['service_name', 'service_machine', 'total_duration', 'duration', 'interval', 'service_description']
        @staticmethod
        def getShowColumns():
                return ['service_name', 'service_machine', 'total_duration', 'duration', 'interval', 'service_description']
       
class ServiceResult(models.Model):
        service_result_name = models.CharField(max_length=200)
        result_date = models.DateTimeField()
        service = models.ForeignKey(Service)
        status = models.CharField(max_length=50)
        
        def __unicode__(self):
                return self.service_result_name

        @staticmethod
        def getColumns():
                return ['service_result_name', 'result_date', 'service', 'status']

        @staticmethod
        def getShowColumns():
                return ['service_result_name', 'result_date', 'service', 'status']
        
        def getPath(self):
                tmp = self.service_result_name.replace(' ', '') + '/'
                return tmp

class ServiceAnalysis(models.Model):
        analysis_name = models.CharField(max_length=200)
        service_result = models.ForeignKey(ServiceResult)
        features_count = models.IntegerField(default=6)
        type = models.CharField(max_length=100)
        status = models.CharField(max_length=50)
        analysis_description = models.CharField(max_length=300)

        def __unicode__(self):
                return self.analysis_name

        @staticmethod
        def getColumns():
                return ['analysis_name', 'service_result', 'features_count', 'type', 'analysis_description']

        @staticmethod
        def getShowColumns():
                return ['analysis_name', 'service_result', 'features_count', 'type', 'status', 'analysis_description']

        def getPath(self):
                tmp = self.service_result.service_result_name.replace(' ', '') + '/' + self.analysis_name.replace(' ', '') + '/'
                return tmp
