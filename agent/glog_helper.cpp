/**
 * @authors Jimmy Sun (yongjie.sun@intel.com)
 * @date    2015-12-01 08:47:47
 * @version 1.0
 */
#include "glog_helper.hpp"

GlogHelper::GlogHelper(const char *program) {
}


GlogHelper::~GlogHelper() {
	google::ShutdownGoogleLogging();
}

const char *logLevelString(LOG_LEVEL  log_level) {
	switch (log_level) {
		case INFO:
			return "INFO";
		case WARN:
			return "WARN";
		case ERROR:
			return "ERROR";
		case FATAL:
			return "FATAL";
	}
}

inline void GlogHelper::log(LOG_LEVEL log_level, const char *log_string) {
	LOG(log_level) << log_string;
}

//inline void GlogHelper::log(LOG_LEVEL log_level, )
void GlogHelper::setLogLevel(LOG_LEVEL log_level) {
	FLAGS_minloglevel = log_level;
	LOG(LOG_LEVEL::INFO) << "Minimal LOG level is " << logLevelString(log_level);
}

void GlogHelper::setLogDir(const char *log_dir) {
	FLAGS_log_dir = log_dir;
	if (access(log_dir, 0) == -1) {
		//log dir is not exist and create it.
		string cmd = "mkdir -p " + log_dir;
		system(cmd.c_str());
	}

	LOG(LOG_LEVEL::INFO) << "PTAP LOG PATH is " << log_dir; 
}