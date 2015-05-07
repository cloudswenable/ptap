PATP performance tracking and analysis platform

PTAP 0.1 is a prototype platform for automate test your program, collect performance data and give out analysis report. It can be used in IPDC domain for BU online/offline test. It can collect many domains performance data like OS-level, Program-level and PMU-level. PMU is server's HW unit named performance monitor unit, many famous performance tools use it like oprofile, perf and intel Vtune.

PTAP has a portal website and client site. A client is an agent runing on testing server response for taking action of test, collect data and pre-processing data. Portal server can create a new test task, dispatch the test job to target servers, collect data from agent and generate report on website.

All function are written by python. Website adopts the Django framework, bootstrap css.

For easily using ptap, we provide some script in "bin", for a try usage, you can deploy the web server and client on the same server and just run "bing/startAll.sh". Also you can deploy ptap on cluster mode with copying all code without the "webserver" to target machine and edit the conf file "clusterService/config/agentclient.cfg", the bellow is a sample:


#Simple Arch
             ----------------
             -              -
             - Web Portal   -
             -              -
             ----------------
                   |
                   |
             ----------------
             -              -
             - Manage Server-
             -              -
             ----------------
                   |
                   |
             -------------------------------          
             |              |              |
             |              |              |
             ------         ------         ------
             -test-         -test-         -test-
             -node-         -node-         -node-
             ------         ------         ------

1. web portal can be deployed in one server, inside the web portal, it has a tcp client to communicate with the manage server
2. manager server can be deployed in one server, it can dispatch the jobs and collect data from test node for web portal query and display
3. Each test node has a agent, to communicate with manage server, to run test job, collect data, and return to manange server

So 3 key config files: web portal: frontendagentclient.cfg,  manage server: server.cfg, test node: agentclient.conf
the three config files are in $ROOT_CODE_DIR/clusterService/config

#sample agentclient config
             [remote-server]
             server_ip = 1.1.1.1
             server_port = 54321
             
             [dispatcher]
             
             [heartbeat-checker]
             interval = 10
             [client]
             client_ip = 2.2.2.2

in the config, we set the central server IP and port for tcp layer and interval 10 seconds for heartbeat check. Current client ip is specific by "client_ip"

#sample server config
             [basic]
             bind_addr = 0.0.0.0
             bind_port = 54321
             epoll_interval = 2
             listen_max = 50
             interval = 20

#sample frontendagentclient config
             [remote-server]
             server_ip = 1.1.1.1
             server_port = 54321

#How to install it.
install Django-1.6.2.tar.gz(https://www.djangoproject.com/download/)
             tar xzvf Django-1.6.2.tar.gz
             cd Django-1.6.2
             sudo python setup.py install

You can install all the python requirements by run `pip install -r requirements.txt`.

install mysql and create a database "performancedb"

run setup.py
             ./setup.py mysql_username mysql_passwd

#Deploy on one server for a try
start server
             bin/startall.py

stop server
             bin/stopall.py

#Deploy on multiple server:
             copy code to each server and run command in "bin/" 
Copyright notice:
  Some license files are include in the root path. PTAP self use the intel sample code license. 

# cli tools
perf-pmu.py can calculate some matrics for the system.
perf-pmu.py -h will print the usage
```shell
[root@ptap-01 exporttools]# ./exporttools/perf-pmu.py -h
/tmp/ptap-experiment/tools/perf -pmu -h -o outfile -r repeatnum [-d delaysecond] [-p pid] -i interval [-n]
```
For example, this command will run perf once for 2 seconds and output the result to output/.
```shell
[root@ptap-01 exporttools]# ./perf-pmu.py -o output/prefix -r 1 -i 2 -p 15312
[root@ptap-01 exporttools]# find output/
output/
output/prefix-20150430172933
output/prefix-20150430172933.out
output/prefix-20150430172933-metric.csv
```
---

perf-hotspots.py can calculate metrics and track events with `perf record` and `perf report` on function level.
Most options have default value.
```shell
[root@ptap-01 exporttools]# ./perf-hotspots.py  -h
Usage: perf-hotspots.py [options]

Options:
  -h, --help            show this help message and exit
  -d DELAY_TIME, --delay=DELAY_TIME
                        time to deplay before start monitor
  -o OUTPATH, --outpath=OUTPATH
                        the file that output will be written
  -u DURATION, --duration=DURATION
                        How long it will monitors
  -r REPEAT, --repeat=REPEAT
                        How many times it will repeats
  -e EVENTS, --events=EVENTS
                        which events it will monitor
  -p PID, --pid=PID     The pid of the process that the monitor will attach to
  -m                    Will the metrics be calculated.
```

If you want to track events on function level for event cpu-clock of process 15312, you can run cmd below.
```shell
[root@ptap-01 exporttools]# ./perf-hotspots.py  -e cpu-clock -p 15312
[root@ptap-01 exporttools]# find outpath/
outpath/
outpath/perf-20150430173649
outpath/report-20150430173649
outpath/20150430173649
```

If you want to calculate metrics on function level of process 15312, you can run cmd below.
```shell
[root@ptap-01 exporttools]# ./perf-hotspots.py  -m -p 15312
[root@ptap-01 exporttools]# find outpath/
outpath/
outpath/perf-20150430173844
outpath/report-20150430173844
outpath/perf-20150430173844-metrics
outpath/report-20150430173844-metrics
outpath/20150430173844
outpath/20150430173844-metrics
```


---

perf-list.py can calculate the metrics like clientService/PerfListMonitor.py
Most options have default value.
```shell
[root@ptap-01 exporttools]# ./perf-list.py -h
Usage: perf-list.py [options]

Options:
  -h, --help            show this help message and exit
  -d DELAY_TIME, --delay=DELAY_TIME
                        time to deplay before start monitor
  -o OUTPATH, --outpath=OUTPATH
                        the file that output will be written
  -u DURATION, --duration=DURATION
                        How long it will monitors
  -r REPEAT, --repeat=REPEAT
                        How many times it will repeats
  -p PID, --pid=PID     The pid of the process that the monitor will attach to
```

If you want to calculate metrics for process 15312, you can run commands below
```shell
[root@ptap-01 exporttools]# ./perf-list.py -p 15312
[root@ptap-01 exporttools]# find outpath/
outpath/
outpath/Raw
outpath/Raw/Events
outpath/Raw/Events/Perf
outpath/Raw/Events/Perf/20150430174330
outpath/Process
outpath/Process/Events
outpath/Process/Events/Perf
outpath/Process/Events/Perf/20150430174330
outpath/Process/Metrics
outpath/Process/Metrics/Perf
outpath/Process/Metrics/Perf/20150430174330
```
