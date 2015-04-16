#!/usr/bin/env python
#-*- coding:utf8 -*-

import sys
from optparse import OptionParser
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from clientService.HotspotsProcessor import HotspotsProcessor, HotspotsProcessorConfig
from clientService.HotspotsMonitor import HotspotsMonitor
from clientService.MonitorAdapter import HotspotsMonitorAdapter


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

    # TODO: process the events
    parser.add_option("-e", "--events", dest="events", default="",
                      help="which events it will monitor", metavar="EVENTS")

    parser.add_option("-p", "--pid", dest="pid", default="",
                      help="The pid of the process that the monitor will attach to", metavar="PID")
    # TODO: type checking. I think it's not safe because of CMD injection
    options, args = parser.parse_args()

    adapter = HotspotsMonitorAdapter(HotspotsMonitor(job_info=options.__dict__),
        HotspotsProcessor(config=HotspotsProcessorConfig(job_info=options.__dict__)))
    adapter.run()


if __name__ == "__main__":
    main()
