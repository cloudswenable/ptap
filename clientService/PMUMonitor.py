import subprocess
from Monitor import *
from PMUMetricsManager import *

class PMUMonitorConfig(MonitorConfig):
	def __init__(self):
		super(PMUMonitorConfig, self).__init__()
		self.rPath = ''
		self.file_name = 'report.dat'

	def getOutputPath(self):
		tmp = self.root_path + '/AllSource/ClientOutput/' + self.rPath + '/Raw/Events/PMU/'
		try:
			shutil.rmtree(tmp)
		except:
			pass
		if not os.path.exists(tmp):
            		os.makedirs(tmp)
		return tmp + self.file_name

class PMUMonitor(Monitor):
	testCommand = 'sudo perf stat -o %s -e %s %s'
        testPidCommand = 'sudo perf stat -o %s -e %s -p %s sleep %s'
	testPlatformCommand = 'sudo perf stat -o %s -a -e %s sleep %s'

        def __init__(self, metricsManager=PMUMetricsManager(), config=PMUMonitorConfig()):
		self.config = config
                self.metricsManager = metricsManager

        def run(self, job):
		self.config.rPath = job.path
		duration = job.pmu_paras['duration']
		delaytime = job.pmu_paras['delay']
		outputPath = self.config.getOutputPath()
                args = [outputPath]
                events = self.metricsManager.getAllEvents()
                args.append(events)
                args.append(duration)
                mCommand = self.testPlatformCommand % tuple(args)
                time.sleep(delaytime)
		out = subprocess.call(mCommand, shell=True)

def main():
        from tmp import Job
        rPath = '/project1/sourcecode1/source/1/test1'
        job = Job(path=rPath, pid='-1', sar_paras={'interval':0,'loops':0}, pmu_paras={'duration':10, 'delay':0}, hotspots_paras={'duration':5}, perf_list_paras={'duration': 10, 'delay': 0})
        monitor = PMUMonitor()
        monitor.run(job)

if __name__ == '__main__':
        main()
