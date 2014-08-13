from MetricsManager import MetricsManager
from MonitorAdapter import MonitorAdapter
from PerfListMonitor import PerfListMonitor
from PerfListProcessor import PerfListProcessor
#from SARMonitor import SARMonitor
#from SARProcessor import SARProcessor
from PMUMonitor import PMUMonitor
from PMUProcessor import PMUProcessor
from Monitor import *
from Processor import *
import shutil

class ServiceMetricsManager(MetricsManager):
        def __init__(self, config=None):
                self.events = ['cpu-cycles', 'instructions', 'cache-misses', 'branch-instructions', 'branch-misses', 'bus-cycles', 'stalled-cycles-frontend', 'stalled-cycles-backend', 'cpu-clock', 'task-clock', 'page-faults', 'context-switches', 'cpu-migrations', 'L1-dcache-loads', 'L1-dcache-load-misses', 'L1-icache-loads', 'L1-icache-load-misses', 'LLC-loads', 'LLC-load-misses', 'LLC-stores', 'LLC-store-misses', 'dTLB-loads', 'dTLB-stores', 'iTLB-loads']

        def getAllEvents(self):
                tmpEventStr = ','.join(self.events)
                return tmpEventStr

class ServicePerfListMonitorConfig(MonitorConfig):
        def __init__(self):
                super(ServicePerfListMonitorConfig, self).__init__()
                self.rPath = ''
                
        def getOutputPath(self):
                tmp = self.root_path + '/AllSource/ClientOutputService/' + self.rPath + '/Raw/Perf/'
                if not os.path.exists(tmp):
                        os.makedirs(tmp)
                return tmp + '/' + time.strftime('%Y%m%d%H%M%S', time.localtime())

        def clearOutputPath(self, rPath):
                tmp = self.root_path + '/AllSource/ClientOutputService/' + rPath
                try:
                        shutil.rmtree(tmp)
                except:
                        pass

class ServicePMUMonitorConfig(MonitorConfig):
        def __init__(self):
                super(ServicePMUMonitorConfig, self).__init__()
                self.rPath = ''
        def getOutputPath(self):
                tmp = self.root_path + '/AllSource/ClientOutputService/' + self.rPath + '/Raw/PMU/'
                if not os.path.exists(tmp):
                        os.makedirs(tmp)
                return tmp + '/' + time.strftime('%Y%m%d%H%M%S', time.localtime())

class ServiceSARMonitorConfig(MonitorConfig):
        def __init__(self):
                super(ServiceSARMonitorConfig, self).__init__()
                self.output_path = ''
                self.sar_interval = ''
                self.sar_loops = ''

        def getOutputPath(self):
                tmp = self.root_path + '/AllSource/ClientOutputService/' + self.output_path + '/Raw/SAR/'
                if not os.path.exists(tmp):
                        os.makedirs(tmp)
                return tmp + '/' + time.strftime('%Y%m%d%H%M%S', time.localtime())

        def toTuple(self):
                return (self.sar_interval, self.sar_loops, self.getOutputPath())
                

class ServicePerfListProcessorConfig(ProcessorConfig):
        def __init__(self):
                super(ServicePerfListProcessorConfig, self).__init__()
                self.rPath = ''

        def getInputPath(self):
                tmp = self.root_path + '/AllSource/ClientOutputService/' + self.rPath + '/Raw/Perf/'
                files = os.listdir(tmp)
                self.fileName = files[-1]
                return tmp + self.fileName
        
        def getOutputPath(self):
                tmp = self.root_path + '/AllSource/ClientOutputService/' + self.rPath + '/Process/Perf/'
                if not os.path.exists(tmp):
                        os.makedirs(tmp)
                return tmp + self.fileName, None
        
        def removeInputFile(self):
                tmp = self.root_path + '/AllSource/ClientOutputService/' + self.rPath + '/Raw/Perf/'
                try:
                        shutil.rmtree(tmp)
                except:
                        pass

class ServicePMUProcessorConfig(ProcessorConfig):
        def __init__(self):
                super(ServicePMUProcessorConfig, self).__init__()
                self.rPath = ''
        def getInputPath(self):
                tmp = self.root_path + '/AllSource/ClientOutputService/' + self.rPath + '/Raw/PMU/'
                files = os.listdir(tmp)
                self.fileName = files[-1]
                return tmp + self.fileName
        def getOutputPath(self):
                tmp = self.root_path + '/AllSource/ClientOutputService/' + self.rPath + '/Process/PMU/'
                if not os.path.exists(tmp):
                        os.makedirs(tmp)
                return tmp + self.fileName, None
        def removeInputFile(self):
                tmp = self.root_path + '/AllSource/ClientOutputService/' + self.rPath + '/Raw/PMU/'
                try:
                        shutil.rmtree(tmp)
                except:
                        pass

class ServiceSARProcessorConfig(ProcessorConfig):
        def __init__(self):
                super(ServiceSARProcessorConfig, self).__init__()
                self.rPath = ''

        def getInputPath(self):
                tmp = self.root_path + '/AllSource/ClientOutputService/' + self.rPath + '/Raw/SAR/'
                files = os.listdir(tmp)
                self.fileName = files[-1]
                return tmp + self.fileName

        def getOutputPath(self):
                tmp = self.root_path + '/AllSource/ClientOutputService/' + self.rPath + '/Process/SAR/'
                if not os.path.exists(tmp):
                        os.makedirs(tmp)
                return tmp + self.fileName

        def removeInputFile(self):
                tmp = self.root_path + '/AllSource/ClientOutputService/' + self.rPath + '/Raw/SAR/'
                try:
                        shutil.rmtree(tmp)
                except:
                        pass

class BackgroundServiceProcessorConfig(ProcessorConfig):
        def __init__(self):
                super(BackgroundServiceProcessorConfig, self).__init__()
                self.rPath = ''
                self.outputFileName = ''
        def getInputPath(self):
                tmp = self.root_path + '/AllSource/ClientOutputService/' + self.rPath + '/Process/'
                return tmp
        def getOutputPath(self):
                tmp = self.root_path + '/AllSource/ClientOutputService/' + self.rPath + '/Final/'
                if not os.path.exists(tmp):
                        os.makedirs(tmp)
                return tmp + self.outputFileName
        def removeInputFile(self):
                tmp = self.root_path + '/AllSource/ClientOutputService/' + self.rPath + '/Process/'
                try:
                        shutil.rmtree(tmp)
                except:
                        pass

class BackgroundServiceProcessor(Processor):
        def __init__(self, config=BackgroundServiceProcessorConfig()):
                super(BackgroundServiceProcessor, self).__init__()
                self.config = config
        def handle(self, job):
                rPath = job.path
                self.config.rPath = rPath
                outputPath = self.config.getOutputPath()
                manager = ResultManager(rootSubPath='/AllSource/ClientOutputService/')
                result = manager.mergeResults(rPath)
                result.name = self.config.outputFileName
                result.path = outputPath
                return [result]
                
class BackgroundServiceMonitorAdapter(MonitorAdapter):
        def __init__(self):
                self.monitorConfig = ServicePerfListMonitorConfig()
                self.perfListMonitor = PerfListMonitor(config=self.monitorConfig)
                self.processorConfig = ServicePerfListProcessorConfig()
                self.perfListProcessor = PerfListProcessor(self.processorConfig)

                self.pMUMonitorConfig = ServicePMUMonitorConfig()
                self.pMUMonitor = PMUMonitor(config=self.pMUMonitorConfig)
                self.pMUProcessorConfig = ServicePMUProcessorConfig()
                self.pMUProcessor = PMUProcessor(config=self.pMUProcessorConfig)

                #self.sARMonitorConfig = ServiceSARMonitorConfig()
                #self.sARMonitor = SARMonitor(self.sARMonitorConfig)
                #self.sARProcessorConfig = ServiceSARProcessorConfig()
                #self.sARProcessor = SARProcessor(self.sARProcessorConfig)

                self.backgroundServiceProcessorConfig = BackgroundServiceProcessorConfig()
                self.backgroundServiceProcessor = BackgroundServiceProcessor(self.backgroundServiceProcessorConfig)
         

        def clearOutputPath(self, job):
                self.monitorConfig.clearOutputPath(job.path)
                
        def startMonitor(self, job):
                self.timestampStr = time.strftime('%Y%m%d%H%M%S', time.localtime())
                self.perfListMonitor.run(job)
                self.pMUMonitor.run(job)

        def startProcessor(self, job):
                self.perfListProcessor.run(job)
                self.pMUProcessor.run(job)
                self.processorConfig.removeInputFile()
                self.pMUProcessorConfig.removeInputFile()
                self.backgroundServiceProcessorConfig.outputFileName = self.timestampStr
                self.backgroundServiceProcessor.run(job)
                self.backgroundServiceProcessorConfig.removeInputFile()

def main():
        from JobDispatcher import Job
        adapter = BackgroundServiceMonitorAdapter()
        job = Job('/test/test', '', -1, perf_list_paras={'duration': 10, 'delay': 1}, pmu_paras={'duration':1, 'delay':1, 'loops': 1})
        adapter.clearOutputPath(job)
        for i in range(2):
                adapter.startMonitor(job)
                adapter.startProcessor(job)

if __name__ == '__main__':
        main()
