#!/usr/bin/env python
#-*- coding:utf8 -*-

import sys
from optparse import OptionParser
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from clientService.PerfListProcessor import PerfListProcessorConfig, PerfListProcessor
from clientService.PerfListMonitor import PerfListMonitor, PerfListConfig
from clientService.MonitorAdapter import PerfListMonitorAdapter


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

    parser.add_option("-p", "--pid", dest="pid", default="",
                      help="The pid of the process that the monitor will attach to", metavar="PID")

    # TODO: type checking. I think it's not safe because of CMD injection
    options, args = parser.parse_args()

    from clientService.tmp import Job
    job = Job(path=options.outpath, pid=options.pid or '-1',
        sar_paras={},
        pmu_paras={},
        hotspots_paras={},
        perf_list_paras={'duration': options.duration, 'delay': options.delay, 'repeat': options.repeat})
    adapter = PerfListMonitorAdapter(PerfListMonitor(config=PerfListConfig(use_base_path=False)),
        PerfListProcessor(config=PerfListProcessorConfig(use_base_path=False)))
    adapter.job = job
    adapter.start()


if __name__ == "__main__":
    main()
