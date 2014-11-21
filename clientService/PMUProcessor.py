from Processor import *
from PMUMetricsManager import PMUMetricsManager
from Util import *
import shutil

class PMUProcessorConfig(ProcessorConfig):
    def __init__(self):
        super(PMUProcessorConfig, self).__init__()
        self.rPath = ''

    def getInputPath(self):
        tmp = 'AllSource/ClientOutput/' + self.rPath + '/Raw/Events/PMU/'
        return self.root_path + '/' + tmp

    def getOutputPath(self):
        tmp = 'AllSource/ClientOutput/' + self.rPath + '/Process/Events/PMU/'
        try:
            shutil.rmtree(tmp)
        except:
            pass
        if not os.path.exists(tmp):
            os.makedirs(tmp)
        tmp2 = 'AllSource/ClientOutput/' + self.rPath + '/Process/Metrics/PMU/'
        try:
            shutil.rmtree(tmp2)
        except:
            pass
        if not os.path.exists(tmp2):
            os.makedirs(tmp2)
        #path = createPaths(self.root_path, tmp)
        #path2 = createPaths(self.root_path, tmp2)
        return tmp, tmp2


class PMUProcessor(Processor):
    regex = '^(\\d+)\\s+(\\w+)'

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
        return (ma.group(1), ma.group(2))

    def getEventsTestDatas(self, inputPath, outputFile):
        eventsDatas = {}
        eventsNames = []
        tmpEventsDatas = []
        input = open(inputPath, 'r')
        timestamp = os.path.basename(inputPath)
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
            eventsResult = CommonDictResult('pmu events', outputFile, timestamp)
            eventsResult.names = eventsNames
            eventsResult.datas = tmpEventsDatas
        return eventsDatas, eventsResult

    def process_file(self, infile, event_out, allMetrics, metrics_out):
        timestamp = infile[-14:]
        eventsDatasDict, eventsResult = self.getEventsTestDatas(infile, event_out)
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
        if metrics_out:
            metricsResult = CommonDictResult('pmu metrics', metrics_out, timestamp)
            metricsResult.names = metricsNames
            metricsResult.datas = metricsDatas
            pmuResults.append(metricsResult)

        for result in pmuResults:
            outfile = open(result.path, 'w')
            outfile.write(result.dumps())
            outfile.close()
            subprocess.call('sudo chmod 777 '+result.path, shell=True)


    def handle(self, job):
        self.config.rPath = job.path
        inputPath = self.config.getInputPath()
        outputPath = self.config.getOutputPath()
        allMetrics = self.metricsManager.getMetrics()

        for file in os.listdir(inputPath):
            self.process_file(inputPath+'/'+file, outputPath[0] +'/' + file, allMetrics, outputPath[1]+'/'+file)

        return [] 

def main():
    from tmp import Job

    rPath = '/project1/sourcecode1/source/1/test1'
    job = Job(path=rPath, pid='-1', sar_paras={'interval': 0, 'loops': 0}, pmu_paras={}, hotspots_paras={'duration': 5},
              perf_list_paras={})
    process = PMUProcessor()
    process.run(job)


if __name__ == '__main__':
    main()
