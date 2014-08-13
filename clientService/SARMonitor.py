__author__ = 'jimmy'

from Monitor import *
from Util import *
import shutil


class SARMonitorConfig(MonitorConfig):
    def __init__(self, sar_interval=2, sar_loops=10):
        super(SARMonitorConfig, self).__init__()
        self.sar_interval = sar_interval
        self.sar_loops = sar_loops
        self.output_path = None

    def getOutputPath(self):
	rPath = 'AllSource/ClientOutput/' + self.output_path + '/Raw/Metrics/SAR/'
	try:
		shutil.rmtree(self.root_path +'/' + rPath)
	except: pass
	tmp = createPaths(self.root_path, rPath) + 'report.dat'
	return tmp
	

    def toTuple(self):
        ret = (self.sar_interval, self.sar_loops, self.getOutputPath())
        return ret


class SARMonitor(Monitor):
    def __init__(self, config=SARMonitorConfig()):
        super(SARMonitor, self).__init__(config)
        self.command = "sar -A %d %d >>%s"

    def run(self, job):
        output_path = job.path
        sar_interval = job.sar_paras['interval']
        sar_loops = job.sar_paras['loops']
        if output_path:
            self.config.output_path = output_path
        if sar_interval:
            self.config.sar_interval = sar_interval
        if sar_loops:
            self.config.sar_loops = sar_loops

        command = self.command % self.config.toTuple()
        subprocess.call(command, shell=True)

def main():
        from tmp import Job
        rPath = '/project1/sourcecode1/source/1/test1'
        job = Job(path=rPath, pid='-1', sar_paras={'interval':1,'loops':1}, pmu_paras={}, hotspots_paras={'duration':5}, perf_list_paras={})
        process = SARMonitor()
        process.run(job)

if __name__ == '__main__':
        main()
