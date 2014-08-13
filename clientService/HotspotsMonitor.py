__author__ = 'jimmy'

from Monitor import *
#from JobDispatcher import Job
from Util import *
import time
import shutil

class HotspotsMonitorConfig(MonitorConfig):

    def __init__(self,  pid=-1, output_path="hotspots.raw"):
        super(HotspotsMonitorConfig, self).__init__()
        self.pid = pid
        self.rPath = ''

    def getOutputPath(self):
	tmp = 'AllSource/ClientOutput/' + self.rPath + '/Raw/Metrics/Hotspots'
	try:
		shutil.rmtree(self.root_path + '/' + tmp)
	except:
		pass
	path = createPaths(self.root_path, tmp)
	return (path+'/perf.data', path+'/report.dat')

    def toTuple(self):
        ret = (self.pid, )
        return ret

class HotspotsMonitor(Monitor):

    def __init__(self):
        super(HotspotsMonitor, self).__init__(config=HotspotsMonitorConfig())
        self.command = 'perf record -p %d -o %s'
        self.recordCommand = 'sudo perf record -a -o %s sleep %s'
	self.reportCommand = 'sudo perf report -i %s >> %s'

    def run(self, job):
	self.config.rPath = job.path
	duration = int(job.hotspots_paras['duration'])
	output1, output2 = self.config.getOutputPath()
	recordCommand = self.recordCommand % (output1, duration)
        p = subprocess.call(recordCommand, shell=True)
	reportCommand = self.reportCommand % (output1, output2)
	subprocess.call(reportCommand, shell=True)
	subprocess.call('sudo chmod 777 '+output1, shell=True)
	subprocess.call('sudo chmod 777 '+output2, shell=True)

def main():
        from tmp import Job
        rPath = '/project1/sourcecode1/source/1/test1'
        job = Job(path=rPath, pid='-1', sar_paras={'interval':0,'loops':0}, pmu_paras={}, hotspots_paras={'duration':5}, perf_list_paras={})
        monitor = HotspotsMonitor()
        monitor.run(job)

if __name__ == '__main__':
        main()
	




