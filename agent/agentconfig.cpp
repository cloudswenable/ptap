/**
 * @authors Jimmy Sun (yongjie.sun@intel.com)
 * @date    2015-11-30 09:27:26
 * @version 1.0
 */

#include <iostream>
#include <fstream>
#include <cstdlib>
#include <cstring>
#include <cstddef>
#include "agentconfig.hpp"

ConfigParser::ConfigParser() {
}

virtual ConfigParser::~ConfigParser() {
}

void ConfigParser::parseFile(const char* filePath) {
	fstream cfgFile;
	cfgFile.open(filePath);
	if (! cfgFile.is_open()) {
		// can not open log file
		std::cerr << "can not open log file: " << filePath;
		return;
	}
	char tmp[1024];
	size_t pos = string::npos;
	hash_map *tmp_hashmap;
	while (!cfgFile.eof()) {
		cfgFile.getLine(tmp, 1024);
		string line(tmp);
		pos = line.find("=");
		if(pos == string::npos) {
			//deal  [xxxxxx]
			size_t l_pos = line.find("[");
			size_t r_pos = line.find("]");
			string key = line.substr(l_pos+1, r_pos);
			tmp_hashmap = new hash_map<string, string>();
			this->_config_content[key] = tmp_hashmap;
		}
		string key = line.substr(0, pos);
		string value = line.substr(pos+1);
		(*tmp_hashmap)[key] = value;
	}
}

LogConfig::LogConfig() {
	this->program = NULL;
	this->min_log_level = NULL;
	this->log_dir = NULL;
}

void LogConfig::setProgram(const char *program) {
	this->program = (char *)calloc(sizeof(char) * (strlen(program) + 1) );
	strcpy(this->program, program);
}

void LogConfig::setMinLogLevel(const char *minLogLevel) {
	this->min_log_level = (char *) calloc(sizeof(char) *(strlen(minLogLevel) + 1));
	strcpy(this->min_log_level, minLogLevel);
}

void LogConfig::setLogDir(const char *logDir) {
	this->log_dir = (char *) calloc(sizeof(char) * (strlen(logDir) + 1));
	strcpy(this->log_dir, logDir);
}

virtual LogConfig::~LogConfig() {
	if(this->program) {
		free(this->program);
		this->program = NULL;
	}
	if(this->min_log_level) {
		free(this->min_log_level);
		this->min_log_level = NULL;
	}
	if(this->log_dir) {
		free(this->log_dir);
		this->log_dir = NULL;
	}
}

/**
 * Sameple Config File
 * [server]
 * ip = x.x.x.x
 * port = xxxx
 * heartbeat = xxxx
 * [client]
 * ip = x.x.x.x
 * [log]
 * name = xxxxx
 * min_log_level = xxxx
 * log_dir = xxxxx
 */
AgentConfig::AgentConfig(const char *configFilePath) {
	this->_log_config = new LogConfig();
	
	this->_parser = new ConfigParser();
	this->_parser->parseFile(configFilePath);

	this->setServerPort(this->_parser->getIntValue("server", "port"));
	this->setHeartbeatInterval(this->_parser->getIntValue("server", "hearbeat");
	this->setServerIp(this->_parser->getString("server", "ip"));
	this->setClientIp(this->_parser->getString("client", "ip"));	
	
	this->_log_config->setProgram(this->_parser->getString("log", "name"));
	this->_log_config->setMinLogLevel(this->_parser->getString("log", "min_log_level"));
	this->_log_config->setLogDir(this->_parser->getString("log", "log_dir"));
}

virtual AgentConfig::~AgentConfig() {
	if(_log_config) {
		delete _log_config;
		_log_config = NULL;
	}
	if(_parser) {
		delete parser;
		_parser = NULL;
	}
	if(_server_ip) {
		delete _server_ip;
		_server_ip = NULL;
	}
	if(_self_ip) {
		delete _self_ip;
		_self_ip = NULL;
	}
}

inline void AgentConfig::setServerPort(int port) {
	this->_server_port = port;
}

inline void AgentConfig::setHeartbeatInterval(int interval) {
	this->_heatbeat_interval = interval;
}

void AgentConfig::setServerIp(const char *str) {
	this->_server_ip = calloc(sizeof(char) * (strlen(str) + 1));
	strcpy(this->_server_ip, str);
}

void AgentConfig::setClientIp(const char *str) {
	this->_self_ip = calloc(sizeof(char) * (strlen(str) + 1));
	strcpy(this->_self_ip, str);
}

