#!/usr/bin/env python

import sys, getopt
import time
import subprocess
import pickle
sys.path.append('../')
from clientService.PMUProcessor import PMUProcessor
from clientService.PMUMetricsManager import *
command = "perf stat -o %s -a -A -x , -e r5300c0,r5302c2,r5302a1,r530208,r531010,r1,r5200c0,r14,r5301c2,rff,r5200c0,r5304c4,r5301a1,rc01,r5301b7,r5301d1,r135,r15301c2,r85,r5381d0,r6,r5380a1,r530151,r0,r5330a1,r43,r335,r53003c,r5321d0,r5301b0,r304,r135,r532024,r52013c,r532010,r53015e,r53013c,r5382d0,r335,r530408,r335,r530ca1,r533079,r15301c2,r5304c5,r530160,r137,r5302ab,r53010e,r301,r86,r335,r530285,r135,r102,r533024,r5307f1,r135,r4,r530479,r135,r153030d,r52003c,r53019c,r534010,r538010,rc04,r530879,r5301a2,r530124,r5,r5302d1,r135,r135,r530449,r530324,r135,r5340a1,r530249,r53400d,r336 %s sleep %s"

def usage():
    print "perf-pmu -h -o outfile -r repeatnum [-d delaysecond] [-p pid] -i interval"

interval = None
output = None
delay = None
repeat = None
pid = None
opts, args = getopt.getopt(sys.argv[1:], "ho:r:d:i:p:")
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
    if op == "-h":
        usage()
        sys.exit

outfiles = []
pidstr = ""
if pid:
    pidstr = " -p %s" % pid
for i in range(0, int(repeat)):
    if delay:
        time.sleep(int(delay))
    timestamp =  time.strftime("%Y%m%d%H%M%S", time.localtime())   
    outfile = output+"-"+timestamp
    outfiles.append(outfile)
    cmd = command % (outfile, pidstr, interval)
    subprocess.call(cmd, shell=True)

processor = PMUProcessor()
events, maps = processor.metricsManager.getAllEvents(True)
for fname in outfiles:
    rawfile = open(fname, 'r')
    resultvalue = {}
    #resultname = {}
    lines = []
        #print code
    for line in rawfile.readlines():
        for code,name in maps.items():
            code = code.replace('r', 'raw 0x')
            line = line.replace(code, name)
            line = line.replace('<not counted>', '0')
            #line = line.replace('colon', ':')
            #line = line.replace('equal', '=')
            line = line.rstrip('\n')
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
