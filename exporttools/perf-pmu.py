#!/usr/bin/env python

import sys, getopt
import time
import subprocess
import pickle
sys.path.append('../')
from clientService.PMUProcessor import PMUProcessor
from clientService.PMUMetricsManager import *
command = "perf stat -o %s -a -A -x , -e %s %s sleep %s"

processor = None
events = None
maps = None

def init(flag):
    global processor 
    global events
    global maps
    processor = PMUProcessor()
    events, maps = processor.metricsManager.getAllEvents(old)

def parseFile(fname):
    rawfile = open(fname, 'r')
    resultvalue = {}
    #resultname = {}
    lines = []
        #print code
    for line in rawfile.readlines():
        for code,name in maps.items():
            if line.find('raw'):
                code = code.replace('r', 'raw 0x')
            line = line.replace(code, name)
            line = line.replace('<not counted>', '0')
            #line = line.replace('colon', ':')
            #line = line.replace('equal', '=')
            line = line.rstrip('\n')
            line = line.rstrip('\r')
        lines.append(line)
    
    for line in lines:
        if not line.startswith('CPU'):
            continue
        datas = line.split(',')
        cpu = datas[0]
        if  resultvalue.get(cpu, None):
            resultvalue[cpu][datas[2]]  = datas[1]
        else:
            resultvalue[cpu] = {}
            resultvalue[cpu][datas[2]]  = datas[1]
    rawfile.close()
    outfile = open(fname+".out", 'w')
    pickle.dump(resultvalue, outfile)
    outfile.close()
    #print resultvalue
    cpuMetrics = {}
    allMetrics = processor.metricsManager.getMetrics()
    outputfile = open(fname+ "-metric.csv", 'w')
    for cpuid,values in resultvalue.iteritems():
        #print values
        #outputfile.write(cpuid+"\n")
        for metric in allMetrics:
            aliasEventDict = processor.metricsManager.getMetricAliasEventDict(metric)
            aliasConstantDict = processor.metricsManager.getMetricAliasConstantDict(metric)
            formula = processor.metricsManager.getMetricFormula(metric)
            for (alias, eventName) in aliasEventDict.iteritems():
                aliasData = values.get(eventName)
                if not aliasData:
                    continue
                formula = formula.replace(alias, aliasData)
            for (alias, constName) in aliasConstantDict.iteritems():
                aliasData = processor.metricsManager.getConstValue(constName)
                if not aliasData: continue
                formula = formula.replace(alias, str(aliasData))
            data = processor.calculater.calculate(formula)
            if data == -1: continue
            if not cpuMetrics.get(cpuid):
                cpuMetrics[cpuid] = {}
            cpuMetrics[cpuid][metric] = data
            #outputfile.write(metric + "," + str(data) + "\n")
    outputfile.write("metric_per_core")
    indexs = []
    for cpuid in cpuMetrics.keys():
        outputfile.write("," + cpuid)
        indexs.append(cpuid)
    outputfile.write("\n")
    for metric in allMetrics:
        outputfile.write(metric)
        for index in indexs:
            outputfile.write("," + str(cpuMetrics[index].get(metric, 0)))
        outputfile.write("\n")
    outputfile.close() 

def parse(infiles):
    if not processor:
        init(old)
    filelist = infiles.split(',')
    for fname in filelist:
        parseFile(fname)

def usage():
    print "perf-pmu -h -o outfile -r repeatnum [-d delaysecond] [-p pid] -i interval [-n]"

interval = None
output = None
delay = None
repeat = None
pid = None
old = True
opts, args = getopt.getopt(sys.argv[1:], "ho:r:d:i:p:nl:")
for op, value in opts:
    if op == "-i":
        interval = value
    if op == "-o":
        output = value
    if op == "-d":
        delay = value
    if op == "-r":
        repeat = value
    if op == "-p":
        pid = value
    if op == "-n":
        old = False
        init(old)
    if op == "-l":
        parse(value)
        sys.exit()
    if op == "-h":
        usage()
        sys.exit()

outfiles = []
pidstr = ""
if pid:
    pidstr = " -p %s" % pid
if not processor:
    init(old)
for i in range(0, int(repeat)):
    if delay:
        time.sleep(int(delay))
    timestamp =  time.strftime("%Y%m%d%H%M%S", time.localtime())   
    outfile = output+"-"+timestamp
    outfiles.append(outfile)
    cmd = command % (outfile, events, pidstr, interval)
    subprocess.call(cmd, shell=True)
for fname in outfiles:
    parse(fname)
