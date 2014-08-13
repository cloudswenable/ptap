from Processor import *
from PMUMetricsManager import PMUMetricsManager
from Util import *

class PMUProcessorConfig(ProcessorConfig):
	def __init__(self):
		super(PMUProcessorConfig, self).__init__()
        	self.rPath = ''

	def getInputPath(self):
        	tmp = 'AllSource/ClientOutput/' + self.rPath + '/Raw/Events/PMU/report.dat'
        	return self.root_path + '/' + tmp

    	def getOutputPath(self):
		tmp = 'AllSource/ClientOutput/' + self.rPath + '/Process/Events/PMU/'
        	tmp2 = 'AllSource/ClientOutput/' + self.rPath + '/Process/Metrics/PMU/'
        	path = createPaths(self.root_path, tmp) + '/report.dat'
        	path2 = createPaths(self.root_path, tmp2) + '/report.dat'
        	return path, path2

class PMUProcessor(Processor):
	regex='^((\\d{1,3},)*\\d{1,3})\\s+(\\w+)'

    	def __init__(self, metricsManager=PMUMetricsManager(), config=PMUProcessorConfig()):
        	super(PMUProcessor, self).__init__()
		self.config = config
        	self.metricsManager = metricsManager
        	self.calculater = Calculater()

    	def handleLine(self, line):
        	pat = re.compile(self.regex)
       		ma = pat.search(line)
        	if not ma:
            		return (None, None)
        	return (ma.group(1), ma.group(3))
	
	def getEventsTestDatas(self, inputPath, outputFile):
        	eventsDatas = {}
                eventsNames = []
                tmpEventsDatas = []
                input = open(inputPath, 'r')
                for line in input:
                    	(data, event) = self.handleLine(line.strip())
                    	if not event: continue
                    	data = data.replace(',', '')
                    	eventsDatas[event] = data
			tmp = event.replace('colon', ':')
			tmp = tmp.replace('equal', '=')
                        eventsNames.append(tmp)
                        tmpEventsDatas.append(float(data))
                input.close()
                eventsResult = None
                if outputFile:
                        eventsResult = CommonDictResult('pmu events', outputFile)
                        eventsResult.names = eventsNames
                        eventsResult.datas = tmpEventsDatas
        	return eventsDatas, eventsResult
	
	def handle(self, job):
		self.config.rPath = job.path
        	inputPath = self.config.getInputPath()
        	outputPath = self.config.getOutputPath()
        	allMetrics = self.metricsManager.getMetrics()

        	eventsDatasDict, eventsResult = self.getEventsTestDatas(inputPath, outputPath[0])
                metricsNames = []
                metricsDatas = []
        	for metric in allMetrics:
            		aliasEventDict = self.metricsManager.getMetricAliasEventDict(metric)
            		formula = self.metricsManager.getMetricFormula(metric)
            		for (alias, eventName) in aliasEventDict.iteritems():
                		aliasData = eventsDatasDict.get(eventName)
                		if not aliasData: continue
                		formula = formula.replace(alias, aliasData)
            		data = self.calculater.calculate(formula)
			if data == -1: continue
                        metricsNames.append(metric)
                        metricsDatas.append(float(data))
                pmuResults = []
                if eventsResult: pmuResults.append(eventsResult)
                if outputPath[1]:
                        metricsResult = CommonDictResult('pmu metrics', outputPath[1])
                        metricsResult.names = metricsNames
                        metricsResult.datas = metricsDatas
                        pmuResults.append(metricsResult)
                return pmuResults

def main():
        from tmp import Job
        rPath = '/project1/sourcecode1/source/1/test1'
        job = Job(path=rPath, pid='-1', sar_paras={'interval':0,'loops':0}, pmu_paras={}, hotspots_paras={'duration':5}, perf_list_paras={})
        process = PMUProcessor()
        process.run(job)

if __name__ == '__main__':
        main()
