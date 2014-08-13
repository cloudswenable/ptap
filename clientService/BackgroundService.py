from JobDispatcher import Job
from BackgroundServiceMonitorAdapter import BackgroundServiceMonitorAdapter
import Queue
import threading
import traceback
import time

class ServiceTask:
        '''
                path: str
                duration: int
                interval: int
        '''
        def __init__(self, path, totalDuration, duration, interval):
                self.path = path
                self.totalDuration = totalDuration
                self.duration = duration
                self.interval = interval

class BackgroundService(threading.Thread):
        def __init__(self, messageHandler):
                super(BackgroundService, self).__init__()
                self.service_queue = Queue.Queue()
                self.messageHandler = messageHandler
        
        def run(self):
                while True:
                        service = self.service_queue.get()
                        if service:
                                self.process(service)

        def process(self, service):
                print 'START MONITOR'
                path = service.path
                allDuration = service.totalDuration
                duration = service.duration
                allInterval = service.interval
                adapter = BackgroundServiceMonitorAdapter()
                job = Job(path, '', -1, perf_list_paras={'duration': duration, 'delay': 0},
                          pmu_paras={'duration':duration, 'delay':0}, rmon_paras={'duration':duration})
                adapter.clearOutputPath(job)
                endTime = time.time() + allDuration
                while time.time() < endTime:
                        adapter.startMonitor(job)
                        adapter.startProcessor(job)
                        time.sleep(allInterval)
                print 'FINISHED'
                self.messageHandler.enqueue({'status': 'done'})

        def dispatch(self, service):
                if service:
                        self.service_queue.put(service)


def main():
        backgroundService = BackgroundService()
        backgroundService.start()
        service = ServiceTask('tttttttttttttt/test', 60, 3)
        backgroundService.dispatch(service)

if __name__ == '__main__':
        main()                 
