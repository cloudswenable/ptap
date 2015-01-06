import json
'''
        0: CommonDictResult
'''

class Result(object):
        '''
                self.type # type of Result
                self.name # name of Result object
                self.path # Result output path
        '''
        def __init__(self, type, name=None, path=None, time=None):
                self.type = type
                self.name = name
                self.path = path
                self.time = time
        def dumps(self): pass
        def loads(self, data): pass
        def query(self, item, scope=None): pass

class CommonDictResult(Result):
        def __init__(self, name=None, path=None, time=None):
                Result.__init__(self, 0, name, path, time)
                self.names = None
                self.datas = None
        def dumps(self):
                return json.dumps([self.type, self.name, self.path, self.time, self.names, self.datas])
        def loads(self, data):
                self.type, self.name, self.path, self.time, self.names, self.datas = json.loads(data)
        def query(self, item, scope=None):
                if scope == "Hotspots":
                    return [(self.names[i], self.datas[i]) for i in range(0,10)]
                count = None
                try:
                        count = self.names.index(item)
                except:
                        pass
                if count==None: return None
                return self.datas[count]

class HotspotResult(Result):
        '''
                self.symbolNames = []
                self.overheadPercentage = [] #total overview percentage
                self.metricsNames = [] #metrics list
                self.metricsCounts = [] #total counts for each metrics
                self.symbolPercentageByMetrics = [[], [], ..] #percentage of each symbol for each metrics
        '''
        def __init__(self, name=None, path=None, time=None):
                Result.__init__(self, 2, name, path, time)
                self.symbolNames = None
                self.overheadPercentage = None
                self.metricsNames = None
                self.metricsCounts = None
                self.symbolPercentageByMetrics = None
        def dumps(self):
                tmp = [self.type, self.name, self.path, self.time, self.symbolNames, self.overheadPercentage, self.metricsNames, self.metricsCounts, self.symbolPercentageByMetrics]
                return json.dumps(tmp)
        def loads(self, data):
                self.type, self.name, self.path, self.time, self.symbolNames, self.overheadPercentage, self.metricsNames, self.metricsCounts, self.symbolPercentageByMetrics = json.loads(data)

class  NMFAnalysisResult(Result):
        def __init__(self, name=None, path=None, time=None):
                Result.__init__(self, 1, name, path, time)
                self.testBelongFeatures = None
                self.featureMetrics = None
                self.featureClasses = None
                self.formatTestsDatas = None
                self.rawTestsDatas = None
        def dumps(self):
                tmp = [self.type, self.name, self.path, self.time, self.testBelongFeatures, self.featureMetrics, self.featureClasses, self.formatTestsDatas, self.rawTestsDatas]
                return json.dumps(tmp)
        def loads(self, data):
                self.type, self.name, self.path, self.time, self.testBelongFeatures, self.featureMetrics, self.featureClasses, self.formatTestsDatas, self.rawTestsDatas = json.loads(data)
        
class AppModelResult(Result):
        '''
                self.cpuDatas = [d1, d2, ....]
                self.memBandwidthDatas = [[d11,d12, ...], [d21, d22...]]
                self.ioUtilDatas = [[d11, d12, ...], [d21, d22, ...]]
                self.netBandwidthDatas = [[d11, d12, ...], [d21, d22, ...]]
        '''
        def __init__(self, name=None, path=None, time=None):
                Result.__init__(self, 3, name, path, time)
                self.cpuDatas = None
                self.memBandwidthDatas = None
                self.ioUtilDatas = None
                self.netBandwidthDatas = None
                self.powerDatas = None
                self.cpu_usage = None
                self.mem_usage = None
                self.disk_usage = None
                self.net_usage = None
        def dumps(self):
                tmp = [self.type, self.name, self.path, self.time, self.cpu_usage, self.disk_usage,
                       self.mem_usage, self.net_usage, self.cpuDatas,
                       self.memBandwidthDatas, self.ioUtilDatas, self.netBandwidthDatas, self.powerDatas]
                return json.dumps(tmp)

        def loads(self, data):
                self.type, self.name, self.path, self.time, self.cpu_usage,\
                self.disk_usage, self.mem_usage, self.net_usage, self.cpuDatas, \
                self.memBandwidthDatas, self.ioUtilDatas, self.netBandwidthDatas, self.powerDatas = json.loads(data)


class SARModelResult(Result):
    '''

    '''
    def __init__(self, name=None, path=None, time=None):
        Result.__init__(self, 4, name, path, time)
        self.cpuMetrics = None
        self.netMetrics = None
        self.memoryMetrics = None
        self.diskMetrics = None
        self.tps= None
        self.tcpMetrics = None
        self.othterMetrics = None
        self.cpuMetricsData = None
        self.netMetricsData = None
        self.memoryMetricsData = None
        self.diskMetricsData = None
        self.tpsData = None
        self.tcpMetricsData = None
        self.otherMetricsData = None

    def getIndex(self, metric):
        if self.cpuMetrics.count(metric) > 0:
            return self.cpuMetricsData, self.cpuMetrics.index(metric)
        if self.netMetrics.count(metric) > 0:
            return self.netMetricsData, self.netMetrics.index(metric)
        if self.memoryMetrics.count(metric) > 0:
            return self.memoryMetricsData, self.memoryMetrics.index(metric)
        if self.diskMetrics.count(metric) > 0:
            return self.diskMetricsData, self.diskMetrics.index(metric)
        if self.tps.count(metric) > 0:
            return self.tpsData, self.tps.index(metric)
        if self.tcpMetrics.count(metric) > 0:
            return self.tcpMetricsData, self.tcpMetrics.index(metric)
        for metrics in self.otherMetrics:
            if metrics.count(metric) > 0:
                return self.otherMetricsData[self.otherMetrics.index(metrics)], metrics.index(metric)
        return None, -1

    def dumpOther(self):
        for i in range(len(self.otherMetrics)):
            print self.otherMetrics[i]
            print self.otherMetricsData[i]
            print "======================="

    def query(self, item, scope=None):
        metric = item
        datas, index = self.getIndex(metric)
        #self.dumpOther()
        if index == -1:
            print "not found metric: ", metric
            return None
        if metric == "%usr":
            value = []
            for vals in datas:
                value.append(vals[index])
            return value
        else:
            return datas[0][index]


    def dumps(self):
        tmp = [self.type, self.name, self.path, self.time, self.cpuMetrics, self.netMetrics, self.memoryMetrics, self.diskMetrics, self.tps, self.tcpMetrics, self.otherMetrics, self.cpuMetricsData, self.netMetricsData, self.memoryMetricsData, self.diskMetricsData, self.tpsData, self.tcpMetricsData, self.otherMetricsData]
        return json.dumps(tmp)
    
    def loads(self, data):
        self.type, self.name, self.path, self.time, self.cpuMetrics, self.netMetrics, self.memoryMetrics, self.diskMetrics, self.tps, self.tcpMetrics, self.otherMetrics, self.cpuMetricsData, self.netMetricsData, self.memoryMetricsData, self.diskMetricsData, self.tpsData, self.tcpMetricsData, self.otherMetricsData = json.loads(data)

