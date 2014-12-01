from MetricsManager import *
import re

class PMUMetricsManagerConfig(MetricsManagerConfig):
        def __init__(self):
                MetricsManagerConfig.__init__(self)
                self.eventsFile = self.config.get('metricsManager', 'PMUMetricsManager_events_file')
                self.metricsFile = self.config.get('metricsManager', 'PMUMetricsManager_metrics_file')

class PMUMetricsManager(MetricsManager):
    def __init__(self, config=PMUMetricsManagerConfig()):
        MetricsManager.__init__(self, config)
        self.eventsDict = \
            EventsParser(configFile=self.eventsFile).getElements()
        self.metricsDict = \
            MetricsParser(configFile=self.metricsFile).getElements()
        self.constDict = self.getConstValues()

    def getConstValues(self):
        tmpDict = {}
        lscpus = os.popen('lscpu').readlines()
        sockets = None
        for line in lscpus:
            if line.startswith('Socket'):
                sockets = int((line.split(':')[1]).strip())
        if sockets:
            tmpDict['system.sockets.count'] = sockets
        cpuinfo = open('/proc/cpuinfo').read()
        pa = re.compile('model name.*:(.*)\n')
        ma = pa.search(cpuinfo)
        cpu_info = ma.group(1).strip()
        start = cpu_info.rfind('@')
        end = cpu_info.rfind('GHz')
        if start > 0 and end > 0:
            cpu_freq = float(cpu_info[start+1:end])
        tmpDict['system.tsc_freq'] = cpu_freq * 1000000000
        return tmpDict
    def getConstValue(self, constName):
        return self.constDict.get(constName)

    def getMetrics(self):
        return self.metricsDict.keys()

    def getRawEventName(self, rawCode):
	rawCode = '0x'+rawCode[1:]
	for name, event in self.eventsDict.items():
		if event.configs[0] == rawCode:
			return name
	return 'null'

    def getAllEvents(self, raw=False):
        str = ''
        rawCodesMap = {}
        for name, event in self.eventsDict.items():
            if raw:
                tmpName = event.getRawEvent()
                rawCodesMap[tmpName] = name
            else:
                tmpName = event.getEvent()
            str += tmpName + ','
        return str[:-1], rawCodesMap

    def getMetricEvents(self, metricName):
        metric = self.metricsDict.get(metricName)
        if metric:
            eventNames = metric.getEvents()
            events = []
            for name in eventNames:
                event = self.eventsDict.get(name)
                if not event:
                    continue
                events.append(event)
            return events
        return []

    def getMetricConstants(self, metricName):
        metric = self.metricsDict.get(metricName)
        if metric:
            return metric.getConstants()
        return []

    def getMetricAliasEventDict(self, metricName):
        metric = self.metricsDict.get(metricName)
        if metric:
            return metric.getAliasEventDict()
        return {}

    def getMetricAliasConstantDict(self, metricName):
        metric = self.metricsDict.get(metricName)
        if metric:
            return metric.getAliasConstantDict()
        return {}

    def getMetricAliasEventName(self, metricName, aliasName):
        metric = self.metricsDict.get(metricName)
        if metric:
            return metric.getAliasEvent(aliasName)
        return None

    def getMetricAliasConstantName(self, metricName, aliasName):
        metric = self.metricsDict.get(metricName)
        if metric:
            return metric.getAliasConstant(aliasName)
        return None

    def getMetricFormula(self, metricName):
        metric = self.metricsDict.get(metricName)
        if metric:
            return metric.getFormula()
        return ''

def main():
        manager = PMUMetricsManager()
	print manager.getRawEventName('r5300c0')
if __name__ == '__main__':
        main()
