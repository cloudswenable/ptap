__author__ = 'ysun49'

from Processor import *
from PerfListMetricsManager import *
from Util import *
import shutil

class PerfListProcessorConfig(ProcessorConfig):
    def __init__(self):
        super(PerfListProcessorConfig, self).__init__()
        self.rPath = ''

    def getInputPath(self):
        tmp = 'AllSource/ClientOutput/' + self.rPath + '/Raw/Events/Perf/'
        return self.root_path + '/' + tmp

    def getOutputPath(self):
        tmp = 'AllSource/ClientOutput/' + self.rPath + '/Process/Events/Perf/'
        try:
            shutil.rmtree(tmp)
        except:
            pass
        if not os.path.exists(tmp):
            os.makedirs(tmp)
        tmp2 = 'AllSource/ClientOutput/' + self.rPath + '/Process/Metrics/Perf/'
        try:
            shutil.rmtree(tmp2)
        except:
            pass
        if not os.path.exists(tmp2):
            os.makedirs(tmp2)
        #path = createPaths(self.root_path, tmp)
        #path2 = createPaths(self.root_path, tmp2)
        return tmp, tmp2


class PerfListProcessor(Processor):
    def __init__(self, config=PerfListProcessorConfig()):
        super(PerfListProcessor, self).__init__()
        self.config = config

    def process(self, inputPath, outputPath):
        timestamp = os.path.basename(inputPath)
        lines = open(inputPath).readlines()
        firstHalf = None
        wholeLine = None
        count = 0
        eventsNames = []
        eventsDatas = []
        metricsNames = []
        metricsDatas = []
        while count < len(lines) - 2:
            rawItems = lines[count][:-1].split(' ')
            items = []
            for item in rawItems:
                if item: items.append(item)
            if items:
                items[0] = items[0].replace(',', '')
            if not items or (not firstHalf and not items[0].replace('.', '').isdigit()):
                count += 1
                continue

            #combine lines
            if not '#' in items:
                firstHalf = items
                wholeLine = None
                count += 1
            elif firstHalf and items[0] == '#':
                wholeLine = firstHalf + items
                firstHalf = None
                count += 1
            elif firstHalf and not items[0] == '#':
                wholeLine = firstHalf
                firstHalf = None
            elif not firstHalf:
                wholeLine = items
                count += 1

            #process lines
            if wholeLine:
                eventsNames.append(wholeLine[1])
                eventsDatas.append(float(wholeLine[0]))
                if len(wholeLine) > 4:
                    tmp = ''
                    for item in wholeLine[4:]:
                        if '[' in item: break
                        tmp += item + ' '
                    if '%' in wholeLine[3]:
                        wholeLine[3] = wholeLine[3][:-1]
                        tmp = tmp + '%'
                    metricsNames.append(wholeLine[1] + '(' + tmp + ')')
                    metricsDatas.append(float(wholeLine[3]))
                wholeLine = None
        perfResults = []
        if outputPath[0]:
            eventsResult = CommonDictResult('perf list events', outputPath[0], timestamp)
            eventsResult.names = eventsNames
            eventsResult.datas = eventsDatas
            perfResults.append(eventsResult)
        if outputPath[1]:
            metricsResult = CommonDictResult('perf list metrics', outputPath[1], timestamp)
            metricsResult.names = metricsNames
            metricsResult.datas = metricsDatas
            perfResults.append(metricsResult)

        for result in perfResults:
            outfile = open(result.path, 'w')
            outfile.write(result.dumps())
            outfile.close()
            subprocess.call('sudo chmod 777 '+result.path, shell=True)

    def handle(self, job):
        self.config.rPath = job.path
        inputPath = self.config.getInputPath()
        outputPath = self.config.getOutputPath()
        for file in os.listdir(inputPath):
            self.process(inputPath+'/'+file, [outputPath[0]+'/'+file, outputPath[1]+'/'+file])

        return [] 


def main():
    from tmp import Job

    rPath = '/project1/sourcecode1/source/1/test1'
    job = Job(path=rPath, pid='-1', sar_paras={'interval': 0, 'loops': 0}, pmu_paras={}, hotspots_paras={'duration': 5},
              perf_list_paras={})
    process = PerfListProcessor()
    process.run(job)


if __name__ == '__main__':
    main()
