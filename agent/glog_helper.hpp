/**
 * @authors Jimmy Sun (yongjie.sun@intel.com)
 * @date    2015-12-01 08:36:44
 * @version 1.0
 */
#ifndef GLOG_HELPER_H 
#define GLOG_HELPER_H

#include "glog-0.3.3/include/glog/logging.h"
#include "glog-0.3.3/include/glog/raw_logging.h"

enum LOG_LEVEL
{
	INFO = google::INFO,
	WARN = google::WARN,
	ERROR = google::ERROR,
	FATAL = google::FATAL,
};

class GlogHelper;
class GlogHelper {
public:
	GlogHelper(const char *program);
	~GlogHelper();

	inline void log(LOG_LEVEL log_level, const char *log_string);
	void setLogLevel(LOG_LEVEL log_level);
	void setLogDir(const char *log_dir);
	void setName(const char *program);

	static GlogHelper *get();
private:
	static GlogHelper *ptap_log;
private:
	const char *name;
};

#endif //GLOG_HELPER_H
