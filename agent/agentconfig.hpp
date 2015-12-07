/**
 * @authors Jimmy Sun (yongjie.sun@intel.com)
 * @date    2015-11-30 09:16:10
 * @version 1.0
 */
#ifndef AGENT_CONFIG_H 
#define AGENT_CONFIG_H

#include <hash_map>

class ConfigParser {
public:
	ConfigParser();
	virtual ~ConfigParser();
	parseFile(const char* filePath);

private:
	hash_map<string, hash_map<string, string>* > _config_content;
};

class LogConfig {
public:
	LogConfig();
	virtual ~LogConfig();
	void setProgram(const char *program);
	void setMinLogLevel(const char *minLogLevel);
	void setLogDir(const char *logDir);

	const char *program;
	const char *min_log_level;
	const char *log_dir;

};

class AgentConfig {

public:
	AgentConfig(const char *configFilePath = "server.cfg");
	virtual ~AgentConfig();
	inline void setServerPort(int port);
	inline void setHeartbeatInterval(int interval);
	void setServerIp(const char *ip);
	void setClientIp(const char *ip);

private:
	const ConfigParser *_parser;
	const char *_server_ip;
	const int _server_port;
	const int _heatbeat_interval;
	const LogConfig *_log_config;
	const char *_self_ip;
};

#endif //AGENT_CONFIG_H
