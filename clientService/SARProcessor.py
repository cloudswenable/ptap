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

    def process(self, inputPath, outputPath):
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
                metricsDatas.append(float(datas[i]))
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
    process.run(job)


if __name__ == '__main__':
    main()
