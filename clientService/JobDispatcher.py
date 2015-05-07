__author__ = 'ysun49'

import Queue
import threading
import traceback

from MonitorAdapter import *
from SourceDeployment import *
from DockerDeployment import DockerDeploymentControler
from Deployment import DeploymentControler, DeploymentControlerConfig
from PMUProcessor import *
from PMUMonitor import *
from SARProcessor import *
from SARMonitor import *
from PerfListMonitor import *
from PerfListProcessor import *
from HotspotsProcessor import *
from HotspotsMonitor import *
from BaiduMonitor import *
from BaiduProcessor import *

class Job(object):
    '''
        pid: -1 platform
        path: relative path
	source_path : relative source path
        pmu_paras: dict {
            duration: int
            loops: int
            delay: int
        }
        sar_paras: dict{
            interval: int
            loops: int
        }
        hotspots_paras: dict{
            duration: int
        }
        perf_list_paras: dict {
	    'duration': int
	    'delay': int
        }
        rmon_paras: dict {
        'duration': int
        }
    '''

    def __init__(self, path, source_path, pid, sar_paras=None, pmu_paras=None, hotspots_paras=None,
                 perf_list_paras=None, rmon_paras=None):
        self.path = path
        self.source_path = source_path
        self.pid = pid
        self.sar_paras = sar_paras
        self.pmu_paras = pmu_paras
        self.hotspots_paras = hotspots_paras
        self.perf_list_paras = perf_list_paras
        self.rmon_paras = rmon_paras

        #TODO add other needed attr

        self.from_cli = False # distinguished with tmp.Job


class JobDispatcher(threading.Thread):
    def __init__(self, responseQueue=None):
        super(JobDispatcher, self).__init__()
        self.job_queue = Queue.Queue()
        self.handler = JobHandler(responseQueue)

    def run(self):
        self.handler.start()
        while True:
            job = self.job_queue.get()
            if job:
                self.handler.handle(job)

    def dispatch(self, job):
        if job:
            self.job_queue.put(job)

    def stopMonitor(self):
        self.handler.stopMonitor()

class JobHandler(threading.Thread):
    def __init__(self, responseQueue):
        threading.Thread.__init__(self)
        self.job_queue = Queue.Queue()
        self.responseQueue = responseQueue
        self.process_steps = []

    def generateSteps(self):
        process_steps = [
            PMUMonitorAdapter(PMUMonitor(), PMUProcessor()),
            PerfListMonitorAdapter(PerfListMonitor(), PerfListProcessor()),
            SARMonitorAdapter(SARMonitor(), SARProcessor()),
            HotspotsMonitorAdapter(HotspotsMonitor(), HotspotsProcessor()),
            #BaiduMonitorAdapter(BaiduMonitor(), BaiduProcessor())
        ]
        return process_steps

    def run(self):
        while True:
            try:
                self.job = self.job_queue.get()
                deployment_type =DeploymentControler.getDeploymentType(self.job.source_path)
                if deployment_type == DeploymentControler.DOCKER:
                    dockerControler = DockerDeploymentControler(self.job.source_path)
                    image_id = dockerControler.build_image()
                    container_id = dockerControler.start(image_id)
                    print "Container:", container_id, "started"
                    pids = dockerControler.get_pids(container_id)
                    pid = pids[0] if pids else None
                elif deployment_type == DeploymentControler.BINARY:
                    #Start source code project
                    sourceCodeControler = SourceDeploymentControler()
                    pid = sourceCodeControler.run(self.job.source_path)
                self.process_steps = self.generateSteps()
                print 'START SOURCE CODE PROCESS PID : ', pid
                if self.job:
                    self.job.pid = pid
                    for step in self.process_steps:
                        step.job = self.job
                        step.start()
                    #for step in self.process_steps:
                    #    step.join()
            except:
                traceback.print_exc()
            print 'JOB DONE'

    def handle(self, job):
        if job:
            self.job_queue.put(job)

    def stopMonitor(self):
        for step in self.process_steps:
            monitor = step.monitor
            if monitor.isAlive():
                monitor.running = False
    
        for step in self.process_steps:
            if step.isAlive():
                step.join()

        self.responseQueue.put({'status': 'done', 'rPath': self.job.path})


def test():
    dispatcher = JobDispatcher()
    dispatcher.start()
    #rPath = '/project1/sourcecode1/source/1/test1'
    rPath = '/Hello_projectname:/Hello_sourcecodename/source/1/start.txt'
    #sPath = '/project1/sourcecode1/source/1'
    sPath = '/Hello_projectname:/Hello_sourcecodename/source/1'
    job = Job(rPath, sPath, pid='-1', sar_paras={'interval': 1, 'loops': 1}, pmu_paras={'duration': 10, 'delay': 0},
              hotspots_paras={'duration': 5}, perf_list_paras={'duration': 10, 'delay': 0})
    dispatcher.dispatch(job)


if __name__ == '__main__':
    test()
