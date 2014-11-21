__author__ = 'jimmy'

import shutil

from Monitor import *

from Util import *


class SARMonitorConfig(MonitorConfig):
    def __init__(self, sar_interval=2, sar_loops=10):
        super(SARMonitorConfig, self).__init__()
        self.sar_interval = sar_interval
        self.sar_loops = sar_loops
        self.output_path = None
        self.file_name = 'report.dat'

    def getOutputPath(self):
        tmp = 'AllSource/ClientOutput/' + self.output_path + '/Raw/Metrics/SAR/'
        try:
            shutil.rmtree(self.root_path + '/' + tmp)
        except:
            pass
        if not os.path.exists(tmp):
            os.makedirs(tmp)
        #tmp = createPaths(self.root_path, rPath) + self.file_name
        return tmp+self.file_name


    def toTuple(self):
        ret = (self.sar_interval, self.sar_loops, self.getOutputPath())
        return ret


class SARMonitor(Monitor):
    def __init__(self, config=SARMonitorConfig()):
        super(SARMonitor, self).__init__(config)
        self.command = "sar -A %d %d >>%s"

    def monitor(self, args):
        command = self.command % tuple(args)
        subprocess.call(command, shell=True)


    def run(self):
        job = self.job
        output_path = job.path
        delaytime = job.pmu_paras['delay']
        sar_interval = job.sar_paras['interval']
        sar_loops = job.sar_paras['loops']
        if output_path:
            self.config.output_path = output_path
        if sar_interval:
            self.config.sar_interval = sar_interval
        if sar_loops:
            self.config.sar_loops = sar_loops
        
        prefix = os.path.dirname(self.config.getOutputPath())
        args = [self.config.sar_interval, self.config.sar_loops, prefix]
        
        while self.running:
            time.sleep(delaytime)
            self.config.file_name = time.strftime('%Y%m%d%H%M%S', time.localtime())
            args[2] = prefix + '/' + self.config.file_name
            self.monitor(args)
            #command = self.command % self.config.toTuple()
            #subprocess.call(command, shell=True)


def main():
    from tmp import Job

    rPath = '/'
    job = Job(path=rPath, pid='-1', sar_paras={'interval': 5, 'loops': 1}, pmu_paras={'delay':5}, hotspots_paras={'duration': 5},
              perf_list_paras={})
    process = SARMonitor()
    process.job = job
    process.start()


if __name__ == '__main__':
    main()
