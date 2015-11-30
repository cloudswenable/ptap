/**
 * @authors Jimmy Sun (yongjie.sun@intel.com)
 * @date    2015-11-30 09:16:10
 * @version 1.0
 */
#ifndef AGENT_CONFIG_H 
#define AGENT_CONFIG_H

class AgentConfig {
public:
	AgentConfig(string configFilePath = "server.cfg");
private:
	const string _server_ip;
	const int _server_port;
	const int _heatbeat_interval;
};

#endif //AGENT_CONFIG_H
