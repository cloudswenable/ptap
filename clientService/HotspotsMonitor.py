__author__ = 'jimmy'

from Monitor import *
#from JobDispatcher import Job
from Util import *
import time
import shutil
# from HotspotsMetricsManager import HotspotsMetricsManager
from PMUMetricsManager import PMUMetricsManager


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
        self.command = 'perf record -p %d -o %s' # what does this used for
        self.useExe = True
        self.job_info = job_info
        # sometimes there is no job instance(e.g. we use the commandline tool perf-hotspots.py ), the job_info will be used
        self.calc_metrics = False
        if job_info is not None:
            self.calc_metrics = job_info['metrics_mode']
        self.metricsManager = PMUMetricsManager()
        # PMUMetricsManager has provided all the functions we need

    def generate_record_cmd(self, duration, events, pid, calc_metrics, output):
        cmd = []
        if self.useExe:
            cmd.append('sudo ' + self.config.root_path + '/tools/perf record')
        else:
            cmd.append("sudo perf record")

        if calc_metrics:
            events, maps = self.metricsManager.getAllEvents(self.useExe)
            cmd.append("-e " + events)
        elif events:
            # The calc_metrics can't be used with specific events
            cmd.append("-e %(events)s")

        if pid:
            cmd.append("-p %(pid)s")
        cmd.append('-a -o %(output)s sleep %(duration)s')
        return ' '.join(cmd) % {"output": output, "duration": duration, "events": events, "pid": pid}

    def generate_report_cmd(self, output1, output2, calc_metrics_mode):
        cmd = []
        if self.useExe:
            cmd.append('sudo ' + self.config.root_path + '/tools/perf report ')
        else:
            cmd.append('sudo perf report ')
        if calc_metrics_mode:
            cmd.append("-n")
        cmd.append('-i %s >> %s')
        return ' '.join(cmd) % (output1, output2)

    def _exec_monitor(self, kwargs, calc_metrics_mode=False):
        metrics_suffix = '-metrics' if calc_metrics_mode else  ""
        recordCommand = self.generate_record_cmd(kwargs["duration"], kwargs["events"], kwargs["pid"], calc_metrics_mode,
            kwargs["output1"] + metrics_suffix)
        p = subprocess.call(recordCommand, shell=True)
        reportCommand = self.generate_report_cmd(kwargs["output1"] + metrics_suffix,
            kwargs["output2"] + metrics_suffix, calc_metrics_mode=calc_metrics_mode)
        subprocess.call(reportCommand, shell=True)
        subprocess.call('sudo chmod 777 ' + kwargs['output1'] + metrics_suffix, shell=True)
        subprocess.call('sudo chmod 777 ' + kwargs['output2'] + metrics_suffix, shell=True)

    def monitor(self, args):
        kwargs = {}
        kwargs["duration"] = args[0]
        kwargs["output1"] = args[1]
        kwargs["output2"] = args[2]
        kwargs["events"] = args[3]
        kwargs["pid"] = args[4]
        
        self._exec_monitor(kwargs, calc_metrics_mode=False)
        if self.calc_metrics:
            self._exec_monitor(kwargs, calc_metrics_mode=True)


    def run(self):
        job = self.job
        #fix bellow in future
        repeat = None # if repeat is None, it will repeat untill running become false
        events = "" # if events is blank, it will use default events
        if job:
            delay = job.perf_list_paras['delay']
            self.config.rPath = job.path
            duration = int(job.hotspots_paras['duration'])
            output1, output2 = self.config.getOutputPath()
            pid = getattr(job, "pid", None)
        elif self.job_info:
            delay = self.job_info.get("delay")
            outpath = self.job_info.get("outpath")
            duration = int(self.job_info.get("duration"))
            repeat = int(self.job_info.get("repeat"))
            events = self.job_info.get("events", "")
            pid = self.job_info.get("pid", None)
            output1, output2 = self.config.getOutputPath(outpath)
        prefix = os.path.dirname(output1)
        args = [duration, output1, output2, events, pid]
        while self.running:
            time.sleep(delay)
            self.config.file_name = 'perf-' + time.strftime('%Y%m%d%H%M%S', time.localtime())
            self.config.output_name = 'report-' + time.strftime('%Y%m%d%H%M%S', time.localtime())
            # TODO hard coding the index here is not good
            args[1] = prefix + '/' + self.config.file_name
            args[2] = prefix + '/' + self.config.output_name
            self.monitor(args)
            if repeat is not None:
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





