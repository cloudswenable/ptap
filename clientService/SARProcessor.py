__author__ = 'ysun49'

from Processor import *
from Util import *
import shutil


class SARProcessorConfig(ProcessorConfig):
    def __init__(self):
        super(SARProcessorConfig, self).__init__()
        self.rPath = ''

    def getInputPath(self):
        tmp = 'AllSource/ClientOutput/' + self.rPath + '/Raw/Metrics/SAR/'
        return self.root_path + '/' + tmp

    def getOutputPath(self):
        tmp = 'AllSource/ClientOutput/' + self.rPath + '/Process/Metrics/SAR/'
        try:
            shutil.rmtree(tmp)
        except:
            pass
        if not os.path.exists(tmp):
            os.makedirs(tmp)
        #path = createPaths(self.root_path, tmp) + '/'
        return tmp


class SARProcessor(Processor):
    def __init__(self, config=SARProcessorConfig()):
        super(SARProcessor, self).__init__()
        self.config = config
        self.indexs = {
            'cpuMetrics': 0,
            'netMetrics': 1,
            'memoryMetrics': 2,
            'diskMetrics': 3,
            'tps': 4,
            'tcpMetrics': 5,
            'others': 6
        }
    
    def getIndex(self, key):
        if key.lower() == "cpu":
            return 0 
        if key.lower() == "dev":
            return 3
        if key.lower() == "iface":
            return 1
        #if key.lower().startswith('kb') or key.lower().startswith('pg'):
        if key.lower().startswith('kb'):
            return 2
        if key.lower() == "tps":
            return 4
        if key.lower().startswith('tcp') or key.lower().startswith('totsck'):
            return 5
        return 6

    def process(self, inputPath, outputPath):
        timestamp = os.path.basename(inputPath)
        discard = True
        newBlock = True
        names = [[],[],[],[],[],[],[]]
        datas = [[],[],[],[],[],[],[]]
        index = 0
        linenum = 0
        again = None
        other_index = 0
        for line in open(inputPath):
            linenum += 1
            if line.startswith('Average'):
                discard = False
            if not discard:
                if not line.strip(' ').rstrip('\n'):
                    newBlock = True
                    continue
                if newBlock:
                    newBlock = False
                    linenum = 0
                    keys = line.split()[1:]
                    index = self.getIndex(keys[0])
                    if index == 6:
                        other_index+=1;
                        names[index].append(keys)
                    else:
                        for key in keys: 
                            if key not in names[index]:
                                names[index].append(key)
                else:
                    #nomal data line
                    innerIndex = -1
                    if  len(datas[index]) >= linenum:
                        again = True
                    else:
                        datas[index].append([])
                        again = False
                    innerIndex = linenum - 1
                    if index == 6:
                        if len(datas[index]) < other_index:
                            datas[index].append([])
                        dataList = line.split()[1:]
                        datas[index][other_index-1].append(dataList)
                        continue
                    if again and index != 2:
                        dataList = line.split()[2:]
                        for data in dataList:
                            datas[index][innerIndex].append(data)
                    else:
                        dataList = line.split()[1:]
                        for data in dataList:
                            datas[index][innerIndex].append(data)

        sarresult = SARModelResult('sar metrics', outputPath, timestamp) 
        sarresult.cpuMetrics = names[0]
        sarresult.netMetrics = names[1]
        sarresult.memoryMetrics = names[2]
        sarresult.diskMetrics = names[3]
        sarresult.tps = names[4]
        sarresult.tcpMetrics = names[5]
        sarresult.otherMetrics = names[6]
        sarresult.cpuMetricsData = datas[0]
        sarresult.netMetricsData = datas[1]
        sarresult.memoryMetricsData = datas[2]
        sarresult.diskMetricsData = datas[3]
        sarresult.tpsData = datas[4]
        sarresult.tcpMetricsData = datas[5]
        sarresult.otherMetricsData = datas[6]
        #sarresult.dumpOther()
        outfile = open(sarresult.path, 'w')
        outfile.write(sarresult.dumps())
        outfile.close()
        subprocess.call('sudo chmod 777 '+sarresult.path, shell=True)

    def process1(self, inputPath, outputPath):
        timestamp = os.path.basename(inputPath)
        inChunk = False
        multiline = False
        prefix = ''
        mid = ''
        titles = None
        datas = None
        formatDatas = []
        metricsNames = []
        metricsDatas = []
        for line in open(inputPath):
            if not line.startswith('Average'):
                inChunk = False
                continue
            rawItems = line[:-1].split(' ')[1:]
            items = []
            for item in rawItems:
                if item: items.append(item)

            if not inChunk:
                inChunk = True
                if items[0].isupper():
                    multiline = True
                    titles = items[1:]
                    prefix = items[0]
                else:
                    multiline = False
                    titles = items
                    prefix = ''
                continue

            if multiline:
                mid = items[0]
                datas = items[1:]
            else:
                mid = ''
                datas = items
            for i in range(len(titles)):
                if prefix and mid:
                    name = (prefix + '_' + mid + '_' + titles[i]).strip()
                else:
                    name = titles[i]
                formatDatas.append((name, datas[i]))
                metricsNames.append(name)
                data = 0.0
                try:
                    data = float(datas[i])
                except:
                    pass
                metricsDatas.append(data)
        metricsResult = CommonDictResult('sar metrics', outputPath, timestamp)
        metricsResult.names = metricsNames
        metricsResult.datas = metricsDatas
        
        outfile = open(metricsResult.path, 'w')
        outfile.write(metricsResult.dumps())
        outfile.close()
        subprocess.call('sudo chmod 777 '+metricsResult.path, shell=True)

    def handle(self, job):
        self.config.rPath = job.path
        inputPath = self.config.getInputPath()
        outputPath = self.config.getOutputPath()
        for file in os.listdir(inputPath):
            self.process(inputPath+'/'+file, outputPath+'/'+file)
        return [] 


def main():
    from tmp import Job

    rPath = '/project1/sourcecode1/source/1/test1'
    job = Job(path=rPath, pid='-1', sar_paras={'interval': 0, 'loops': 0}, pmu_paras={}, hotspots_paras={'duration': 5},
              perf_list_paras={})
    process = SARProcessor()
    process.process("/home/jimmy/result.sar", None)


if __name__ == '__main__':
    main()
