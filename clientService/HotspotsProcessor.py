__author__ = 'ysun49'

from Processor import *
from Util import *
import shutil


class HotspotsProcessorConfig(ProcessorConfig):
    def __init__(self):
        super(HotspotsProcessorConfig, self).__init__()
        self.rPath = ''

    def getInputPath(self):
        tmp = 'AllSource/ClientOutput/' + self.rPath + '/Raw/Metrics/Hotspots/'
        return self.root_path + '/' + tmp

    def getOutputPath(self):
        tmp = 'AllSource/ClientOutput/' + self.rPath + '/Process/Metrics/Hotspots/'
        try:
            shutil.rmtree(tmp)
        except:
            pass
        if not os.path.exists(tmp):
            os.makedirs(tmp)
        #path = createPaths(self.root_path, tmp) + '/'
        return tmp


class HotspotsProcessor(Processor):
    def __init__(self):
        super(HotspotsProcessor, self).__init__()
        self.config = HotspotsProcessorConfig()

    def process(self, inputPath, outputPath):
        timestamp = os.path.basename(inputPath)
        tmpNames = []
        tmpDatas = []
        for line in open(inputPath):
            if line.startswith('#'):
                continue
            if not line.strip():
                continue

            line = line[:-1]
            rawItems = line.split(' ')
            items = []
            for item in rawItems:
                if item: items.append(item)
            name = ' '.join(items[1:]) + '%'
            data = items[0][:-1]
            tmpNames.append(name)
            tmpDatas.append(float(data))
        result = CommonDictResult('hotspots', outputPath, timestamp)
        result.names = tmpNames
        result.datas = tmpDatas
        outfile = open(result.path, 'w')
        outfile.write(result.dumps())
        outfile.close()
        subprocess.call('sudo chmod 777 '+result.path, shell=True)

    def handle(self, job):
        self.config.rPath = job.path
        inputPath = self.config.getInputPath()
        outputPath = self.config.getOutputPath()
        for file in os.listdir(inputPath):
            if file.startswith("report"):
                self.process(inputPath+'/'+file, outputPath+'/'+ file[7:])
        return [] 

def main():
    from tmp import Job

    rPath = '/project1/sourcecode1/source/1/test1'
    job = Job(path=rPath, pid='-1', sar_paras={'interval': 0, 'loops': 0}, pmu_paras={}, hotspots_paras={'duration': 5},
              perf_list_paras={})
    process = HotspotsProcessor()
    process.run(job)


if __name__ == '__main__':
    main()
