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
        def query(self, item): pass

class CommonDictResult(Result):
        def __init__(self, name=None, path=None, time=None):
                Result.__init__(self, 0, name, path, time)
                self.names = None
                self.datas = None
        def dumps(self):
                return json.dumps([self.type, self.name, self.path, self.time, self.names, self.datas])
        def loads(self, data):
                self.type, self.name, self.path, self.time, self.names, self.datas = json.loads(data)
        def query(self, item):
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

