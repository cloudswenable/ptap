from ResultManager import *
import re


IFACE_REG = re.compile("^\s*?(\S+)\s*:")


def get_net_ifaces(without_lo=True):
    ifaces = []
    with open('/proc/net/dev') as f:
        for line in f.readlines():
            iface_name = IFACE_REG.findall(line)
            if iface_name:
                iface_name = iface_name[0]
                ifaces.append(iface_name)
    return ifaces


def get_iface_keys(without_lo=True):
    '''
    this function will read the local interface names and return results like this
    ['IFACE_lo_rxkB/s','IFACE_lo_txkB/s','IFACE_eth0_rxkB/s','IFACE_eth0_txkB/s','IFACE_eth1_rxkB/s','IFACE_eth1_txkB/s']
    '''
    if_keys = []
    for key_pattern in ('IFACE_%s_rxkB/s','IFACE_%s_txkB/s'):
        for iface_name in get_net_ifaces(without_lo=without_lo):
            if_keys.append(key_pattern % iface_name)
    return if_keys


class ResultAdapter(object):
        def getModelsAnalysisResults(self, rPath):
                chartNames = ['cpu utilization', 'mem read', 'mem write', 'io read', 'io write', 'net read', 'net write', 'cpu power', 'mem power']
                modelNames = ['cpu model', 'mem model', 'disk model', 'net model']
                modelSummary = ['cpu model', 'mem model', 'disk model', 'net model']
                modelMetrics = [['CPI', 'stalled-cycles-frontend(frontend cycles idle %)'], \
                                ['cache-misses(% of all cache refs )', 'DTLB store MPI'], \
                                ['IO_bandwidth_disk_or_network_reads(M/s)'], \
                                ['IO_bandwidth_disk_or_network_reads(M/s)']]
                manager = ResultManager()
                rawDatas, rawUsages = manager.queryAppModelResult(rPath)
                datas = []
                count = 0
                for items in rawDatas:
                        tmpList = []
                        for item in items:
                                tmpList.append([chartNames[count], item])
                                count += 1
                        datas.append(tmpList)
                max = -1
                modelIndex = -1
                for i in range(len(rawUsages)):
                        if max<rawUsages[i]:
                                max = rawUsages[i]
                                modelIndex = i
                modelName = modelNames[modelIndex]
                datas.append(modelName)
                datas.append(modelSummary[modelIndex])
                metrics = manager.queryResultsByNames(rPath, modelMetrics[modelIndex])
                datas.append(metrics)
                return datas

        def getNMFAnalysisServiceInputs(self, rPath):
                manager = ResultManager(rootSubPath='/AllSource/ServerOutputService', tailSubPath='/Final')
                manager.getOutputResults(rPath)
                rawDatas = []
                rawMetricNames = []
                allTestNames = []
                results = manager.results
                if results:
                        rawMetricNames = results[0].names
                for result in results:
                        rawDatas.append(result.datas)
                        allTestNames.append(result.name)
                return (rawDatas, rawMetricNames, allTestNames)

        def getNMFAnalysisServiceResults(self, rPath):
                manager = ResultManager(rootSubPath='/AllSource/ServerOutputService', tailSubPath='/ServerFinal')
                manager.getOutputResults(rPath)
                results = manager.results
                tmpStr = ''
                if results:
                        result = results[0]
                        tmpStr = {'testFeatures': result.testBelongFeatures,\
                                 'metrics': result.featureMetrics,\
                                 'features': result.featureClasses,\
                                 'tests': result.formatTestsDatas,\
                                 'rawTests': result.rawTestsDatas}
                return tmpStr

        def getAnalysisResult(self, rPaths, metrics=None, formula=None, scope=None):
                datas = []
                manager = ResultManager()
                #print "metrics", metrics
                #print "formula", formula
                for rPath in rPaths:
                        if formula:
                                value = manager.queryResultByFormula(rPath, formula, metrics, scope)
                                datas.append(value)
                        else:
                                values = manager.queryResultsByNames(rPath, metrics, scope)
                                if scope and scope == "Hotspots":
                                    for value in values:
                                        datas.append(value)
                                else:
                                    for value in values:
                                        datas.append(value[1])
                #print datas
                return datas
        
        def getSingleResultOverview(self, rPath):
                items = ['cache-misses(% of all cache refs )', 'branch-misses(of all branches %)', 'task-clock(CPUs utilized )', 'LLC-load-misses(of all LL-cache hits %)', 'CPI', 'L1-dcache-load-misses(of all L1-dcache hits %)']
                manager = ResultManager()
                datas = manager.queryResultsByNames(rPath, items)
                return datas
        
        def getResultsByEachTable(self, rPaths, tables, limits):
                results = []
                #init
                for i in range(len(tables)):
                        tmpDatas = []
                        for j in range(limits[i][1]-limits[i][0]):
                                tmpDatas.append([])
                        results.append((tables[i], tables[i].replace(' ', ''), tmpDatas))
                #get datas
                for path in rPaths:
                        manager = ResultManager()
                        for i in range(len(tables)):
                                datas = manager.queryTable(path, tables[i], limits[i][0], limits[i][1])
                                for j in range(len(datas)):
                                        if not results[i][2][j]: results[i][2][j].append(datas[j][0])
                                        results[i][2][j].append(datas[j][1])
                return results
        
        def getSARResult(self, rpath):
            manager = ResultManager()
            return manager.querySARModelResult(rpath)

        def getOverviewResults(self, rPaths):
                tables = [('application performance',[], 0),('micro-arch performance',['CPI', 'cache-misses(% of all cache refs )', 'branch-misses(of all branches %)', 'mem Page Hits vs. all requests'], 0),('os level performance',['cswch/s','INTR_sum_intr/s','tps',] + get_iface_keys(), 0),('application hotspots', [0,1,2,3,4], 1, 'hotspots')]
                #init
                results = []
                for table in tables:
                        tableName = table[0]
                        tableItems = table[1]
                        tmpDatas = []
                        for item in tableItems:
                                tmpDatas.append([])
                        results.append((tableName, tmpDatas))
                #fetch datas
                for path in rPaths:
                        manager = ResultManager()
                        for i in range(len(tables)):
                                table = tables[i]
                                tableName = table[0]
                                tableItems = table[1]
                                type = table[2]
                                rawTableName = None
                                itemsResults = None
                                if type == 1:
                                        rawTableName = table[3]
                                        itemsResults = manager.queryResultsByIndexes(path, rawTableName, tableItems)
                                else:
                                        itemsResults = manager.queryResultsByNames(path, tableItems)
                                for j in range(len(itemsResults)):
                                        if not results[i][1][j]: results[i][1][j].append(itemsResults[j][0])
                                        results[i][1][j].append(itemsResults[j][1])
                return results
        
        def getDynamicOverviewResults(self, rPath, qtables=None, starts=None, next=1):
                size =3 
                tables = [
                    ('micro-arch performance',
                     ['CPI', 'cache-misses(% of all cache refs )', 'branch-misses(of all branches %)', 'mem Page Hits vs. all requests'],
                     0),
                    ('os level performance',
                     ['cswch/s','INTR_sum_intr/s','tps',] + get_iface_keys(),
                     0),
                ]
                results = []
                manager = ClassifyResultManager(rootSubPath='/AllSource/ServerOutput/', tailSubPath='/Process')
                manager.getOutputResults(rPath)
                if not qtables:
                        qtables = ['micro-archperformance', 'oslevelperformance']
                        starts = [0, 0]
                for i in range(len(qtables)):
                        table = None
                        for tmpTable in tables:
                                if tmpTable[0].replace(' ', '') == qtables[i]:
                                        table = tmpTable
                                        break
                        if not table: continue
                        if int(next):
                                tmpStart = int(starts[i])
                                tmpEnd = int(starts[i])+size
                        else:
                                tmpStart = int(starts[i])-2*size
                                if tmpStart<0: tmpStart = 0
                                tmpEnd = tmpStart+size
                        tmpDatas = manager.queryResultsByNames(table[1], tmpStart, tmpEnd)
                        tmpavg = []
                        for items in tmpDatas:
                                tmpSum = 0
                                for item in items:
                                        tmpSum += item
                                if len(items):
                                        tmpavg.append(tmpSum/len(items))
                                else:
                                        tmpavg.append(0)
                        times = []
                        tmptmpStart = tmpStart
                        if tmpDatas:
                                for j in range(len(tmpDatas[0])):
                                        tmptmp = str(tmptmpStart+j)
                                        times.append(tmptmp+'s')
                        results.append([table[0], table[1], tmpavg, tmpDatas, times, tmpEnd])
                return results

def main():
        rPath = 'project1/sourcecode1/source/1/test5/'
        adapter = ResultAdapter()
        results = adapter.getDynamicOverviewResults(rPath)
        print results

if __name__ == '__main__':
        main()

                
