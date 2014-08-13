PATP performance tracking and analysis platform

PTAP 0.1 is a prototype platform for automate test your program, collect performance data and give out analysis report. It can be used in IPDC domain for BU online/offline test. It can collect many domains performance data like OS-level, Program-level and PMU-level. PMU is server's HW unit named performance monitor unit, many famous performance tools use it like oprofile, perf and intel Vtune.

PTAP has a portal website and client site. A client is an agent runing on testing server response for taking action of test, collect data and pre-processing data. Portal server can create a new test task, dispatch the test job to target servers, collect data from agent and generate report on website.

All function are writted by python. Website adopts the Django framework, bootstrap css.

For easily using ptap, we provide some script in "bin", for a try usage, you can deploy the web server and client on the same server and just run "bing/startAll.sh". Also you can deploy ptap on cluster mode with copying all code without the "webserver" to target machine and edit the conf file "clusterService/config/agentclient.cfg", the bellow is a sample:

##sample config
[remote-server]
server_ip = 10.240.192.112
server_port = 54321

[dispatcher]

[heartbeat-checker]
interval = 10 

in the config, we set the central server IP and port for tcp layer and interval 10 seconds for heartbeat check.

Copyright notice:
  Some license files are include in the root path. PTAP self use the intel sample code license. 

