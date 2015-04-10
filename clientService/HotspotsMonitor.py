__author__ = 'jimmy'

from Monitor import *
#from JobDispatcher import Job
from Util import *
import time
import shutil


class HotspotsMonitorConfig(MonitorConfig):
    def __init__(self, pid=-1, output_path="hotspots.raw"):
        super(HotspotsMonitorConfig, self).__init__()
        self.pid = pid
        self.rPath = ''
        self.file_name = 'perf.data'
        self.output_name = 'report.dat'

    def getOutputPath(self, outpath=None):
        tmp = outpath or ('AllSource/ClientOutput/' + self.rPath + '/Raw/Metrics/Hotspots')
        try:
            shutil.rmtree(self.root_path + '/' + tmp)
        except:
            pass
        if not os.path.exists(tmp):
            os.makedirs(tmp)
        #path = createPaths(self.root_path, tmp)
        return (tmp + '/' + self.file_name, tmp + '/' + self.output_name)

    def toTuple(self):
        ret = (self.pid, )
        return ret


class HotspotsMonitor(Monitor):
    def __init__(self, job_info=None):
        super(HotspotsMonitor, self).__init__(config=HotspotsMonitorConfig())
        self.command = 'perf record -p %d -o %s'
        self.recordCommand = 'sudo perf record -a -o %(output)s sleep %(duration)s'
        self.recordCommandWithEvents = 'sudo perf record -a -e %(events)s -o %(output)s sleep %(duration)s'
        self.useExe = True
        self.recordCommandExe = 'sudo ' + self.config.root_path + '/tools/perf record -a -o %(output)s sleep %(duration)s'
        self.recordCommandExeWithEvents = 'sudo ' + self.config.root_path + '/tools/perf record -a -e %(events)s -o %(output)s sleep %(duration)s'
        self.reportCommand = 'sudo perf report -i %s >> %s'
        self.reportCommandExe = 'sudo ' + self.config.root_path + '/tools/perf report -i %s >> %s'
        self.job_info = job_info
        # sometimes there is no job instance(e.g. we use the commandline tool perf-hotspots.py ), the job_info will be used


    def monitor(self, args):
        # TODO I think it will be better to use keyword arguments...
        duration = args[0]
        output1 = args[1]
        output2 = args[2]
        events = args[3]

        if self.useExe:
            tmpCommand = self.recordCommandExeWithEvents if events else self.recordCommandExe
            tmpReportCommand = self.reportCommandExe
        else:
            tmpCommand = self.recordCommandWithEvents if events else self.recordCommand
            tmpReportCommand = self.reportCommand

        recordCommand = tmpCommand % {"output": output1, "duration": duration, "events": events}
        p = subprocess.call(recordCommand, shell=True)

        reportCommand = tmpReportCommand % (output1, output2)
        subprocess.call(reportCommand, shell=True)
        subprocess.call('sudo chmod 777 ' + output1, shell=True)
        subprocess.call('sudo chmod 777 ' + output2, shell=True)

    def run(self):
        job = self.job
        #fix bellow in future
        repeat_times = None # if repeat_time is None, it will repeat untill running become false
        events = "" # if events is blank, it will use default events
        if job:
            delay = job.perf_list_paras['delay']
            self.config.rPath = job.path
            duration = int(job.hotspots_paras['duration'])
            output1, output2 = self.config.getOutputPath()
        elif self.job_info:
            delay = self.job_info.get("delay")
            outpath = self.job_info.get("outpath")
            duration = int(self.job_info.get("duration"))
            repeat = int(self.job_info.get("repeat"))
            events = self.job_info.get("events", "")
            output1, output2 = self.config.getOutputPath(outpath)
        prefix = os.path.dirname(output1)
        args = [duration, output1, output2, events]
        while self.running:
            time.sleep(delay)
            self.config.file_name = 'perf-' + time.strftime('%Y%m%d%H%M%S', time.localtime())
            self.config.output_name = 'report-' + time.strftime('%Y%m%d%H%M%S', time.localtime())
            # TODO hard coding the index here is not good
            args[1] = prefix + '/' + self.config.file_name
            args[2] = prefix + '/' + self.config.output_name
            self.monitor(args)
            if repeat:
                repeat -= 1
                if repeat == 0:
                    self.running = False



def main():
    from tmp import Job

    rPath = '/project1/sourcecode1/source/1/test1'
    job = Job(path=rPath, pid='-1', sar_paras={'interval': 0, 'loops': 0}, pmu_paras={}, hotspots_paras={'duration': 5},
              perf_list_paras={})
    monitor = HotspotsMonitor()
    monitor.run(job)


if __name__ == '__main__':
    main()





