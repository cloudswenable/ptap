/**
 * @authors Jimmy Sun (yongjie.sun@intel.com)
 * @date    2015-11-30 08:47:03
 * @version 1.0
 */
#ifndef AGENT_H_
#define AGENT_H_

#include "agentconfig.hpp"
#include "glog_helper.hpp"

GlogHelper *ptap_log = GlogHelper::get();

class Agent {
public:
	Agent();
	Agent(const char *configFilePath);

private:
	/** command port for upd connection*/
	const int _cmd_port;
	/** data transfer port for tcp connection */
	int _data_port;
	/** server configuration */
	AgentConfig _config;
	static GlogHelper *ptap_log;
};

#endif // AGENT_H
