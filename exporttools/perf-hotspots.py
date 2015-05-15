#!/usr/bin/env python
#-*- coding:utf8 -*-

import sys
from optparse import OptionParser
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from clientService.HotspotsProcessor import HotspotsProcessor, HotspotsProcessorConfig
from clientService.HotspotsMonitor import HotspotsMonitor
from clientService.MonitorAdapter import HotspotsMonitorAdapter
from clientService.PerfListMetricsManager import PerfListMetricsManager, PerfListMetricsManagerConfig
from clientService.Monitor import MonitorConfig
import subprocess
import re


NOT_SUPPORTED_EVENTS = set((
    "L1-dcache-prefetches",
    "L1-icache-loads",
    "L1-icache-prefetches",
    "L1-icache-prefetch-misses",
    "dTLB-prefetches",
    "dTLB-prefetch-misses",
))


def main():
    parser = OptionParser()
    parser.add_option("-d", "--delay", dest="delay", default=0,
                      help="time to deplay before start monitor", metavar="DELAY_TIME")

    parser.add_option("-o", "--outpath", dest="outpath", default="outpath",
                      help="the file that output will be written", metavar="OUTPATH")

    parser.add_option("-u", "--duration", dest="duration", default=2,
                      help="How long it will monitors", metavar="DURATION")

    parser.add_option("-r", "--repeat", dest="repeat", default=1,
                      help="How many times it will repeats", metavar="REPEAT")

    parser.add_option("-e", "--events", dest="events", default="",
                      help="which events it will monitor", metavar="EVENTS")

    parser.add_option("-p", "--pid", dest="pid", default="",
                      help="The pid of the process that the monitor will attach to", metavar="PID")

    parser.add_option("-m", action="store_true", dest="metrics_mode", help="Will the metrics be calculated.",
        default=False)

    parser.add_option("-l", action="store_true", dest="use_perf_list_events",
        help="This will use perf-list events", default=False)

    # TODO: type checking. I think it's not safe because of CMD injection
    options, args = parser.parse_args()

    if options.use_perf_list_events:
        # options.events = PerfListMetricsManager(PerfListMetricsManagerConfig()).getAllEvents()
        events = get_valid_events()
        # FIXME: if we specify pid, we found it will report
        # such error "Fatal: --mmap_pages/-m value must be a power of two."
        # So if we specify pid, we only cpu-cycles without cpu-clock
        if options.pid:
            events = filter(lambda x: x not in CONFLICT_EVENTS, events)
        options.events = ",".join(events)

    adapter = HotspotsMonitorAdapter(
        HotspotsMonitor(job_info=options.__dict__),
        HotspotsProcessor(config=HotspotsProcessorConfig(job_info=options.__dict__),
            calc_metrics=options.__dict__.get("metrics_mode"))
    )
    adapter.run()


def get_valid_events():
    '''
    This function will return the perf list events including [Hardware event],
    [Software event] and  [Hardware cache event].
    '''
    event_pattern = re.compile(r"^\s+(\S+).*\[(Hardware|Software|Hardware cache) event\]")
    perf_exec = MonitorConfig().root_path + '/tools/perf'
    output = subprocess.check_output([perf_exec, 'list'])
    events = []
    for line in output.splitlines():
        event = event_pattern.findall(line)
        if event and event[0][0] not in NOT_SUPPORTED_EVENTS:
            events.append(event[0][0])
    return events


# utils function
# FIXME
def find_conflict_functions():
    '''
    when using perf record with -p, using some events together will report
    error 'Fatal: --mmap_pages/-m value must be a power of two.'
    So this functions will find which events are conflict with previous events
    '''
    perf_exec = MonitorConfig().root_path + '/tools/perf'
    events = get_valid_events()
    last_events = []
    conflict_events = []
    for event in events:
        last_events.append(event)
        args = [perf_exec, 'record', "-e", ','.join(last_events), '-p', '15312', '-o', 'data', '-a', 'sleep', '1']
        # args = [perf_exec, 'list']
        # print " ".join(args)
        # retcode = subprocess.check_output(" ".join(args))
        retcode = subprocess.call(args)
        if retcode != 0:
            conflict_events.append(event)
            last_events.pop(-1)
        # retcode = subprocess.call(args)
        print last_events
        print retcode
    print conflict_events

# At last, we found CONFLICT_EVENTS
CONFLICT_EVENTS = set(['cpu-clock', 'task-clock', 'page-faults', 'minor-faults', 'major-faults',
'context-switches', 'cpu-migrations', 'alignment-faults', 'emulation-faults'])


if __name__ == "__main__":
    main()
