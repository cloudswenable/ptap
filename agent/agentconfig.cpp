/**
 * @authors Jimmy Sun (yongjie.sun@intel.com)
 * @date    2015-11-30 09:27:26
 * @version 1.0
 */
#include <fstream>
#include <iostream>
#include "agentconfig.hpp"

AgentConfig::AgentConfig(const char *configFilePath) {
	fstream cfgFile;
	cfgFile.open(configFilePath);
	if (! cfgFile.is_open()) {

	}
}