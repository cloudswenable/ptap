import subprocess

from Monitor import *
from PMUMetricsManager import *
import shutil


class PMUMonitorConfig(MonitorConfig):
    def __init__(self):
        super(PMUMonitorConfig, self).__init__()
        self.rPath = ''
        self.file_name = 'report.dat'

    def getOutputPath(self):
        tmp = self.root_path + '/AllSource/ClientOutput/' + self.rPath + '/Raw/Events/PMU/'
        try:
            shutil.rmtree(tmp)
        except Exception as e:
            pass
        if not os.path.exists(tmp):
            os.makedirs(tmp)
        return tmp + self.file_name


class PMUMonitor(Monitor):
    def __init__(self, metricsManager=PMUMetricsManager(), config=PMUMonitorConfig()):
        Monitor.__init__(self, config)
        self.metricsManager = metricsManager
        self.testCommand = 'sudo perf stat -o %s -e %s %s'
        self.testPidCommand = 'sudo perf stat -o %s -e %s -p %s sleep %s'
        self.testPlatformCommand = 'sudo perf stat -o %s -a -e %s sleep %s'
        self.testPlatformCommandExe = 'sudo ' + self.config.root_path + '/tools/perf stat -o %s -a -e %s sleep %s'
        self.useExe = True

    def preprocess(self, path, maps):
        subprocess.call('sudo chmod 777 ' + path, shell=True)
        rfile = open(path, 'r')
        context = rfile.read()
        rfile.close()
        for code, name in maps.items():
            context = context.replace(code, name)
        rfile = open(path, 'w')
        rfile.write(context)
        rfile.close()

    def monitor(self, args):
        if self.useExe:
            tmpCommand = self.testPlatformCommandExe
        else:
            tmpCommand = self.testPlatformCommand
        mCommand = tmpCommand % tuple(args[0:3])
        out = subprocess.call(mCommand, shell=True)
        outputPath = args[0]
        maps = args[3]
        if self.useExe:
            self.preprocess(outputPath, maps)

    def run(self):
        self.config.rPath = self.job.path
        duration = self.job.pmu_paras['duration']
        delaytime = self.job.pmu_paras['delay']
        prefix = os.path.dirname(self.config.getOutputPath())
        args = [prefix]
        events, maps = self.metricsManager.getAllEvents(self.useExe)
        args.append(events)
        args.append(duration)
        args.append(maps)
        while self.running:
            time.sleep(delaytime)
            self.config.file_name = time.strftime('%Y%m%d%H%M%S', time.localtime())
            args[0] = prefix + '/' + self.config.file_name
            self.monitor(args)


def main():
    from tmp import Job

    rPath = '/project1/sourcecode1/source/1/test1'
    job = Job(path=rPath, pid='-1', sar_paras={'interval': 0, 'loops': 0}, pmu_paras={'duration': 10, 'delay': 0},
              hotspots_paras={'duration': 5}, perf_list_paras={'duration': 10, 'delay': 0})
    monitor = PMUMonitor()
    monitor.run(job)


if __name__ == '__main__':
    main()
