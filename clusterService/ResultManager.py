import os
from ResultModel import *
from Util import Calculater
import re

class AbstractResultManager(object):
        def __init__(self, rootSubPath='/AllSource/ServerOutput/', tailSubPath='/Process'):
                self.rootPath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                self.resultPath = self.rootPath + rootSubPath
                self.tailSubPath = tailSubPath

        def createResult(self, content):
                result = None
                if not content: return result
                if content.startswith('[0'):
                        result = CommonDictResult()
                        result.loads(content)
                elif content.startswith('[1'):
                        result = NMFAnalysisResult()
                        result.loads(content)
                elif content.startswith('[3'):
                        result = AppModelResult()
                        result.loads(content)
                elif content.startswith('[4'):
                        result = SARModelResult()
                        result.loads(content)
                return result

        def initResults(self, path, scope=None):
                print "real path: ", path
                files = []
                try:
                        files = os.listdir(path)
                        files.sort()
                except: pass
                for file in files:
                        realPath = path + '/' + file
                        if os.path.isdir(realPath):
                                self.initResults(realPath,scope)
                                continue
                        if scope:
                            if realPath.find(scope) == -1:
                                continue
                        content = open(realPath).read()
                        result = self.createResult(content)
                        if result:
                                self.addResults(result)

        def addResults(self, result): pass

        def getOutputResults(self, rPath, scope=None): 
                tmpPath = self.resultPath+'/'+rPath+'/'+self.tailSubPath
                self.initResults(tmpPath, scope)

class ClassifyResultManager(AbstractResultManager):
        def __init__(self, rootSubPath='/AllSource/ServerOutput/', tailSubPath='/Process'):
                super(ClassifyResultManager, self).__init__(rootSubPath, tailSubPath)
                self.results = {}

        def addResults(self, result):
                if self.results.has_key(result.name):
                        self.results[result.name].append(result)
                else:
                        self.results[result.name] = []

        def queryResultsByNames(self, names, start, end):
                datas = []
                for name in names:
                        tmpData = []
                        for listName, resultslist in self.results.items():
                                if resultslist and resultslist[0].query(name):
                                        for result in resultslist:
                                                tmpDataItem = result.query(name)
                                                if not tmpDataItem:
                                                        tmpDataItem = 0
                                                tmpData.append(float(tmpDataItem))
                                        break
                        if not tmpData:
                                count = len(self.results.items()[0][1])
                                tmpData = [0]*count
                        datas.append(tmpData[start:end])
                return datas 

class ResultManager(AbstractResultManager):
        def __init__(self, rootSubPath='/AllSource/ServerOutput/', tailSubPath='/Process'):
                super(ResultManager, self).__init__(rootSubPath, tailSubPath)
                self.results = []

        def addResults(self, result):
                self.results.append(result)
                
        def mergeResults(self, rPath):
                self.getOutputResults(rPath)
                names = []
                datas = []
                for result in self.results:
                        if result.type != 0: continue
                        names += result.names
                        datas += result.datas
                mergeResult = CommonDictResult()
                mergeResult.names = names
                mergeResult.datas = datas
                return mergeResult

        def getCPUFreq(self):
            cpuinfo = open('/proc/cpuinfo').read()
            pa = re.compile('model name.*:(.*)\n')
            ma = pa.search(cpuinfo)
            cpu_info = ma.group(1).strip()
            start = cpu_info.rfind('@')
            end = cpu_info.rfind('GHz')
            cpu_freq = 0
            if start > 0 and end > 0:
                cpu_freq = float(cpu_info[start+1:end])
            return cpu_freq 

        def queryResultsByNames(self, rPath, items, scope=None):
                self.getOutputResults(rPath, scope)
                datas = []
                print "query: ", items
                for item in items:
                        if item == "CPU_all_MHz":
                            freq = self.getCPUFreq() * 1000
                            datas.append((item, freq))
                            continue
                        found = False
                        for result in self.results:
                                data = result.query(item, scope)
                                if data and scope == "Hotspots":
                                    return data
                                    break
                                if data and type(data)==list:
                                    for d in data:
                                        d = float(d)
                                        datas.append((item, d))
                                    found = True
                                    break

                                elif data is not None: 
                                        data = float(data)
                                        datas.append((item, data))
                                        found = True
                                        break
                        if not found: datas.append((item, 0))
                return datas     

        def queryResultsByIndexes(self, rPath, tableName, indexes):
                self.getOutputResults(rPath)
                result = None      
                datas=[]
                for result in self.results:
                        if result.name == tableName:
                            for index in indexes:
                                datas.append((result.names[index], result.datas[index]))
                            return datas
                return datas

        def queryTable(self, rPath, tableName, start, end):
                self.getOutputResults(rPath)
                result = None
                datas = []
                for result in self.results:
                        if result.name == tableName:
                            for i in range(end-start):
                                if start+i < len(result.names):
                                    datas.append((result.names[start+i], result.datas[start+i]))
                            break;
                return datas

        def queryResultByFormula(self, rPath, formula, parameters, scope=None):
                rawdatas = self.queryResultsByNames(rPath, parameters, scope)
                datas = [item[1] for item in rawdatas]
                formula = (formula % tuple(datas)).strip()
                try:
                        if datas.index(-1)>=0: return None
                except: pass
                cal = Calculater()
                value = cal.calculate(formula)
                return value

        def queryAppModelResult(self, rPath):
                self.getOutputResults(rPath)
                result = None
                found = 0 
                for result in self.results:
                        if result.type == 3:
                                found = 1
                                break
                datas = []
                usages = []
                if found:
                        datas.append(result.cpuDatas)
                        datas.append(result.memBandwidthDatas)
                        datas.append(result.ioUtilDatas)
                        datas.append(result.netBandwidthDatas)
                        datas.append(result.powerDatas)
                        usages.append(result.cpu_usage)
                        usages.append(result.mem_usage)
                        usages.append(result.disk_usage)
                        usages.append(result.net_usage)
                return datas, usages
        
        def querySARModelResult(self, rPath):
            self.getOutputResults(rPath)
            result = None
            found = 0
            for result in self.results:
                if result.type == 4:
                    found = 1
                    break

            metricsName = []
            metricsData = []
            #TODO to display more modify here
            tags = ['sar cpu', 'sar net', 'sar memory', 'sar disk', 'sar tps']
            ret = [[],[],[],[],[]]
            if found:
                ret[0].append(tags[0])
                ret[0].append(result.cpuMetrics)
                ret[0].append(result.cpuMetricsData)
                ret[1].append(tags[1])
                ret[1].append(result.netMetrics)
                ret[1].append(result.netMetricsData)
                ret[2].append(tags[2])
                ret[2].append(result.memoryMetrics)
                ret[2].append(result.memoryMetricsData)
                ret[3].append(tags[3])
                ret[3].append(result.diskMetrics)
                ret[3].append(result.diskMetricsData)
                ret[4].append(tags[4])
                ret[4].append(result.tps)
                ret[4].append(result.tpsData)

            return ret 
def main():
        manager = ResultManager()
        '''
        manager = ClassifyResultManager()
        rPath = '/'
        print '+++++++++++++++++++++++++++++++++++++++++'
        manager.getOutputResults(rPath)
        print manager.results
        names = ['CPI', 'cache-misses(% of all cache refs )', 'cswch/s']
        datas = manager.queryResultsByNames(names)
        print datas
        '''
        manager.getOutputResults('/sssssssss/SSSs/source/1.0/Sssssssss/')
        for result in manager.results:
            print result.name
            print result.datas
        datas = manager.queryResultsByIndexes('/sssssssss/SSSs/source/1.0/Sssssssss/','hotspots',[1,2,3,4])
        print datas
if __name__ == '__main__':
        main()
