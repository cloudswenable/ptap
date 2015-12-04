/**
 * @authors Jimmy Sun (yongjie.sun@intel.com)
 * @date    2015-11-30 09:27:26
 * @version 1.0
 */

#include <iostream>
#include <fstream>
#include <cstdlib>
#include "agentconfig.hpp"

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


AgentConfig::AgentConfig(const char *configFilePath) {
	fstream cfgFile;
	cfgFile.open(configFilePath);
	if (! cfgFile.is_open()) {
		// can not open log file
		std::cerr << "can not open log file: " << configFilePath;
		return;
	}


}