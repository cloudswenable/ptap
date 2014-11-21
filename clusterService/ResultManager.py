import os
from ResultModel import *
from Util import Calculater

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
                return result

        def initResults(self, path):
                files = []
                try:
                        files = os.listdir(path)
                        files.sort()
                except: pass
                for file in files:
                        realPath = path + '/' + file
                        if os.path.isdir(realPath):
                                self.initResults(realPath)
                                continue
                        content = open(realPath).read()
                        result = self.createResult(content)
                        if result:
                                self.addResults(result)

        def addResults(self, result): pass

        def getOutputResults(self, rPath): 
                tmpPath = self.resultPath+'/'+rPath+'/'+self.tailSubPath
                self.initResults(tmpPath)

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

        def queryResultsByNames(self, rPath, items):
                self.getOutputResults(rPath)
                datas = []
                for item in items:
                        found = False
                        for result in self.results:
                                data = result.query(item)
                                if data: 
                                        data = float(data)
                                        datas.append((item, data))
                                        found = True
                                        break
                        if not found: datas.append((item, 0))
                return datas     

        def queryResultsByIndexes(self, rPath, tableName, indexes):
                self.getOutputResults(rPath)
                result = None      
                for result in self.results:
                        if result.name == tableName:
                                break;
                datas = []
                if not result: return datas
                for index in indexes:
                        datas.append((result.names[index], result.datas[index]))
                return datas
      
        def queryTable(self, rPath, tableName, start, end):
                self.getOutputResults(rPath)
                result = None
                for result in self.results:
                        if result.name == tableName:
                                break
                datas = []
                if not result: return datas
                for i in range(end-start):
                        if start+i < len(result.names):
                                datas.append((result.names[start+i], result.datas[start+i]))
                return datas

        def queryResultByFormula(self, rPath, formula, parameters):
                rawdatas = self.queryResultsByNames(rPath, parameters)
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
                

def main():
        manager = ClassifyResultManager()
        rPath = '/project1/sourcecode1/source/1/test5/'
        print '+++++++++++++++++++++++++++++++++++++++++'
        manager.getOutputResults(rPath)
        print manager.results
        names = ['CPI', 'cache-misses(% of all cache refs )', 'cswch/s']
        datas = manager.queryResultsByNames(names)
        print datas

if __name__ == '__main__':
        main()
