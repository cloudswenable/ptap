__author__ = 'ysun49'

from Processor import *
from Util import *

class HotspotsProcessorConfig(ProcessorConfig):
    def __init__(self):
	super(HotspotsProcessorConfig, self).__init__()
	self.rPath = ''
    
    def getInputPath(self):
	tmp = 'AllSource/ClientOutput/' + self.rPath + '/Raw/Metrics/Hotspots/report.dat'
	return self.root_path + '/' + tmp
   
    def getOutputPath(self):
	tmp = 'AllSource/ClientOutput/' + self.rPath + '/Process/Metrics/Hotspots/'
        path = createPaths(self.root_path, tmp) + '/report.dat'
        return path


class HotspotsProcessor(Processor):

    def __init__(self):
        super(HotspotsProcessor, self).__init__()
	self.config = HotspotsProcessorConfig()

    def process(self, inputPath, outputPath):
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
        result = CommonDictResult('hotspots', outputPath)
        result.names = tmpNames
        result.datas = tmpDatas
        return [result]

    def handle(self, job):
	self.config.rPath = job.path
	inputPath = self.config.getInputPath()
	outputPath = self.config.getOutputPath()
	return self.process(inputPath, outputPath)
        
def main():
        from tmp import Job
        rPath = '/project1/sourcecode1/source/1/test1'
        job = Job(path=rPath, pid='-1', sar_paras={'interval':0,'loops':0}, pmu_paras={}, hotspots_paras={'duration':5}, perf_list_paras={})
        process = HotspotsProcessor()
        process.run(job)

if __name__ == '__main__':
        main()
