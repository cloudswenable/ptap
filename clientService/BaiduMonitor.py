__author__ = 'jimmy'

from Monitor import *
from Util import *
import shutil


class BaiduMonitorConfig(MonitorConfig):

    def __init__(self):
        super(BaiduMonitorConfig, self).__init__()
        self.rPath = ''
        self.tool_path = '/tools/rmon/'

    def getOutputPath(self):
        tmp = 'AllSource/ClientOutput/' + self.rPath + '/Raw/Metrics/RMON'
        try:
            shutil.rmtree(self.root_path + '/' + tmp)
        except:
            pass
        path = createPaths(self.root_path, tmp)
        return (path+'report.dat')

class BaiduMonitor(Monitor):

    def __init__(self):
        super(BaiduMonitor, self).__init__(config=BaiduMonitorConfig())
        self.command = 'sudo ' + self.config.root_path + self.config.tool_path + 'rmon -p %d -t %d >>%s'
        #print self.command

    def run(self, job):
        self.config.rPath = job.path
        duration = int(job.rmon_paras['duration'])
        cmd = self.command % (job.pid, duration, self.config.getOutputPath())
        print cmd, duration
        child = subprocess.Popen(cmd, shell=True)
        child.wait()


def main():
    from tmp import Job
    rPath = '/project1/sourcecode1/source/1/test1'
    job = Job(path=rPath, pid=6614, sar_paras={'interval':1,'loops':1}, pmu_paras={},
              hotspots_paras={'duration':5}, perf_list_paras={}, rmon_paras={'duration':5})
    process = BaiduMonitor()
    process.run(job)

if __name__ == '__main__':
    main()
