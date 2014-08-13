#!/usr/bin/python
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.generic import View
from django.shortcuts import render
from showControler.models import *
import sys
from function_views import frontendAgent

##############################################
############# Views ##########################
##############################################

class SystemShowView(View):
	system_content_page = 'showControler/pages/system_content.html'

	def get(self, request, *args, **kwargs):
		models = MachineModel.objects.all()
		machines = []
		count = 1
		for model in models:
			name = model.name
			cutline = False
			if count % 4 == 0: cutline = True
			count += 1
			attrs = []
			attrs.append(('mac', model.mac))
			attrs.append(('active', model.active))
			attrs.append(('ip', model.ip))
			attrs.append(('fileno', model.fileno))
			attrs.append(('os info', model.os_info))
			attrs.append(('cpu info', model.cpu_info))
			attrs.append(('mem info', model.mem_info))
			attrs.append(('disk info', model.disk_info))
			attrs.append(('ht', model.ht))
			attrs.append(('turbo', model.turbo))
			machines.append((name, cutline, attrs))
				
		context = {'system': True, 'machines': machines}
		return render(request, self.system_content_page, context)

class ClearMachinesView(View):
	def get(self, request, *args, **kwargs):
		modelMachine = MachineModel.objects.all()
		for model in modelMachine:
			if not model.active:
				model.delete()
		return HttpResponseRedirect(reverse('showControler:system', args=()))
		

class SyncMachinesView(View):
	def get(self, request, *args, **kwargs):
		modelMachine = MachineModel.objects.all()
		existips = [machine.ip for machine in modelMachine if machine.active]
		localDeadIps = [machine.ip for machine in modelMachine if not machine.active]
		machinesInfo = {'ips': existips, }
                #print '+++++++++++++++++++++++ existips = ', existips
                #print '+++++++++++++++++++++++ localDeadIps = ', localDeadIps

		machines, deadMachines = frontendAgent.fetchMachines(machinesInfo)
		deadIps = deadMachines['ips']
                #print '+++++++++++++++++++++++++++ deadIps = ', deadIps
		for model in modelMachine:
			if model.ip in deadIps:
				model.active = False
				model.save()
                #print '+++++++++++++++++++++++ machines = ', machines
		for machine in machines:
			ip = machine['ip']
			if ip in localDeadIps:
				tmpMachine = MachineModel.objects.filter(ip=ip)[0]
                                tmpMachine.fileno = machine['fileno']
				tmpMachine.active = True
				tmpMachine.save()
				continue
                        name = machine['name']
                        fileno = machine['fileno']
			mac = machine['mac']
			os_info = machine['os_info']
			cpu_info = machine['cpu_info']
			mem_info = machine['mem_info']
			disk_info = machine['disk_info']
			ht = machine['ht']
			turbo = machine['turbo']
			tmp = MachineModel(name=name, active=True, mac=mac, ip=ip, fileno=fileno, os_info=os_info, cpu_info=cpu_info, mem_info=mem_info, disk_info=disk_info, ht=ht, turbo=turbo)
			tmp.save()
		return HttpResponseRedirect(reverse('showControler:system', args=()))
