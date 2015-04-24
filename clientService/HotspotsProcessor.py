__author__ = 'ysun49'

from Processor import *
from Util import *
import shutil
import re
from PMUMetricsManager import PMUMetricsManager


class HotspotsProcessorConfig(ProcessorConfig):
    def __init__(self, job_info=None):
        super(HotspotsProcessorConfig, self).__init__(job_info=job_info)
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
    def __init__(self, config=HotspotsProcessorConfig(), calc_metrics=False):
        super(HotspotsProcessor, self).__init__(config=config)
        self.calc_metrics = calc_metrics
        self.metricsManager = PMUMetricsManager()
        self.calculater = Calculater()

    def _process_normal(self, inputPath, outputPath):
        filename = os.path.basename(inputPath)
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
        result = CommonDictResult('hotspots', outputPath, filename)
        result.names = tmpNames
        result.datas = tmpDatas
        outfile = open(result.path, 'w')
        outfile.write(result.dumps())
        outfile.close()
        subprocess.call('sudo chmod 777 '+result.path, shell=True)

    def _process_metrics(self, inputPath, outputPath):
        code_pattern = re.compile(r"^# Events: \d+  raw (0x\w+)$")
        samples_pattern = re.compile(r'^\s+\S+\s+(\d+)\s+(\S.*)$')
        data = {}
        events, maps = self.metricsManager.getAllEvents(True)
        # collect the values for the files first
        with open(inputPath) as f:
            for line in f.readlines():
                codes = code_pattern.findall(line)
                if codes:
                    code = codes[0]
                    name = maps['r' + code[2:]]
                samples =samples_pattern.findall(line)
                if samples:
                    sample, key = samples[0]
                    if not data.has_key(key):
                        data[key] = {}
                    data[key][name] = sample

        # calculate and orgnize the metrics
        allMetrics = self.metricsManager.getMetrics()
        finalMetrics = {}
        for key, fdata in data.items():
            for metric in allMetrics:
                if not finalMetrics.has_key(metric):
                    finalMetrics[metric] = {}
                aliasEventDict = self.metricsManager.getMetricAliasEventDict(metric)
                aliasConstantDict = self.metricsManager.getMetricAliasConstantDict(metric)
                formula = self.metricsManager.getMetricFormula(metric)
                for (alias, eventName) in aliasEventDict.iteritems():
                    aliasData = fdata.get(eventName)
                    if not aliasData:
                        # getting None means there is 0 event for this function
                        aliasData = "0"
                    formula = formula.replace(alias, aliasData)
                for (alias, constName) in aliasConstantDict.iteritems():
                    aliasData = self.metricsManager.getConstValue(constName)
                    if not aliasData: continue
                    formula = formula.replace(alias, str(aliasData))
                data = self.calculater.calculate(formula)
                if data == -1: continue
                finalMetrics[metric][key] = data

        # ouput the metrics
        with open(outputPath, "w") as f:
            for metric, data in finalMetrics.items():
                f.write("# %s\n" % metric)
                def _cmp(x, y):
                    x = float(x[1])
                    y = float(y[1])
                    if x > y:
                        return -1
                    elif x < y:
                        return 1
                    else:
                        return 0
                
                for key, value in sorted(data.items(), cmp=_cmp):
                    f.write("%s, %s\n" % (key, value))

    def process(self, inputPath, outputPath, calc_metrics):
        if calc_metrics:
            self._process_metrics(inputPath, outputPath)
        else:
            self._process_normal(inputPath, outputPath)

    def handle(self, job_or_job_info):
        # if isinstance(job_or_job_info, Job): 
        if isinstance(job_or_job_info, dict):
            job_info = job_or_job_info
            inputPath = outputPath = job_info.get("outpath")
        else:
            job = job_or_job_info
            self.config.rPath = job.path
            inputPath = self.config.getInputPath()
            outputPath = self.config.getOutputPath()
        for file in os.listdir(inputPath):
            if file.startswith("report"):
                self.process(inputPath+'/'+file, outputPath+'/'+ file[7:], file.endswith("metrics"))
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
