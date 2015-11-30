/**
 * @authors Jimmy Sun (yongjie.sun@intel.com)
 * @date    2015-11-30 08:47:03
 * @version 1.0
 */
#ifndef AGENT_H_
#define AGENT_H_

#include "agentconfig.hpp"

class Agent {
public:
	Agent();
	Agent(string configFilePath);

private:
	/** command port for upd connection*/
	const int _cmd_port;
	/** data transfer port for tcp connection */
	int _data_port;
	/** server configuration */
	AgentConfig _config;
};

#endif // AGENT_H
