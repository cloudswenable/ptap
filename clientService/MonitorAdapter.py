__author__ = 'jimmy'

from Monitor import *

class MonitorAdapter(threading.Thread):

    def __init__(self, monitor, processor):
        threading.Thread.__init__(self)
        self.monitor = monitor
        self.processor = processor
        self.job = None

    def run(self):
        self.monitor.job = self.job
        self.monitor.start()
        self.monitor.join()

        self.processor.job = self.job
        self.processor.start()
        self.processor.join()

    def startMonitor(self, job):
        self.monitor.run(job)

    def startProcessor(self, job):
        self.processor.run(job)

class PMUMonitorAdapter(MonitorAdapter):

    def __init__(self, pmu_monitor, pmu_processor):
        super(PMUMonitorAdapter, self).__init__(pmu_monitor, pmu_processor)

class SARMonitorAdapter(MonitorAdapter):

    def __init__(self, sar_monitor, sar_processor):
        super(SARMonitorAdapter, self).__init__(sar_monitor, sar_processor)

class HotspotsMonitorAdapter(MonitorAdapter):
    def __init__(self, hotspots_monitor, hotspots_processor):
        super(HotspotsMonitorAdapter, self).__init__(hotspots_monitor, hotspots_processor)

class PerfListMonitorAdapter(MonitorAdapter):

    def __init__(self, perf_list_monitor, perf_list_processor):
        super(PerfListMonitorAdapter, self).__init__(perf_list_monitor, perf_list_processor)

class BaiduMonitorAdapter(MonitorAdapter):

    def __init__(self, baidu_monitor, baidu_processor):
        super(BaiduMonitorAdapter, self).__init__(baidu_monitor, baidu_processor)



