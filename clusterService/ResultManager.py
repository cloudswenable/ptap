import os
from ResultModel import *
from Util import Calculater
class ResultManager(object):
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
                                self.results.append(result)
                
        def getOutputResults(self, rPath):
                self.results = []
                tmpPath = self.resultPath+'/'+rPath+'/'+self.tailSubPath
                self.initResults(tmpPath)

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
        manager = ResultManager()
        rPath = '/project1/sourcecode1/source/1/test1/'
        print '+++++++++++++++++++++++++++++++++++++++++'
        items = ['CPI', 'cpu-cycles(GHz )', 'uncacheable reads PI', 'LLC-misses(of all LL-cache hits %)']
        datas = manager.queryResults(rPath, items)
        print datas

if __name__ == '__main__':
        main()
