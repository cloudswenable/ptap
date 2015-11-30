/**
 * @authors Jimmy Sun (yongjie.sun@intel.com)
 * @date    2015-11-30 09:16:10
 * @version 1.0
 */
#ifndef SERVER_CONFIG_H 
#define SERVER_CONFIG_H

class ServerConfig {
public:
	ServerConfig(string configFilePath = "server.cfg");
private:
	const string _server_ip;
	const int _server_port;
	const int _heatbeat_interval;
};

#endif //SERVER_CONFIG_H
