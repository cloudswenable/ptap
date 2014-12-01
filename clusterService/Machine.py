__author__ = 'jimmy'

import struct
class Machine(object):
    name = ''
    mac = 'none'
    ip_addr = ''
    fileno = ''
    os_info = ''
    cpu_info = ''
    mem_info = ''
    disk_info = ''
    ht = False
    turbo = False
    others = ''

    def toString(self):
        fmt = '%ss%ss%ss%ss%ss%ss%ss%ss%ss??' % (len(self.name), len(self.mac), len(self.ip_addr), len(self.fileno), 
                                        len(self.os_info), len(self.cpu_info),
                                        len(self.mem_info), len(self.disk_info), len(self.others))
        pack_fmt = struct.pack('i%ds'% len(fmt), len(fmt), fmt)

        return pack_fmt + struct.pack(fmt, self.name, self.mac, self.ip_addr, self.fileno, self.os_info,
                           self.cpu_info, self.mem_info, self.disk_info, self.others, self.ht, self.turbo)

    #TODO finish it
    def fromString(self, fmt_str, str):
        fmts = fmt_str.split("s")
	name_len = int(fmts[0])
	if name_len:
	    self.name = struct.unpack('%ds'%(name_len), str[0:name_len])[0]	

        mac_len = int(fmts[1])
	start = name_len
        if mac_len:
            self.mac = struct.unpack('%ds'%(mac_len), str[start:start+mac_len])[0]

        ip_len = int(fmts[2])
        start += mac_len
        if ip_len:
            self.ip_addr = struct.unpack('%ds'%(ip_len), str[start:start+ip_len])[0]

	fileno_len = int(fmts[3])
	start += ip_len
	if fileno_len:
	    self.fileno = struct.unpack('%ds' % (fileno_len), str[start: start+fileno_len])[0]

        os_info_len = int(fmts[4])
        start += fileno_len
        if os_info_len:
            self.os_info = struct.unpack('%ds'%(os_info_len), str[start:start+os_info_len])[0]

        start += os_info_len
        cpu_info_len = int(fmts[5])
        if cpu_info_len:
            self.cpu_info = struct.unpack('%ds'%(cpu_info_len), str[start:start+cpu_info_len])[0]

        start += cpu_info_len
        mem_info_len = int(fmts[6])
        if mem_info_len:
            self.mem_info = struct.unpack('%ds'%(mem_info_len), str[start:start+mem_info_len])[0]

        start += mem_info_len
        disk_info_len = int(fmts[7])
        if disk_info_len:
            self.disk_info = struct.unpack('%ds'%(disk_info_len), str[start:start+disk_info_len])[0]

        start += disk_info_len
        others_len = int(fmts[8])
        if others_len:
            self.others = struct.unpack('%ds'%(others_len), str[start:start+others_len])[0]

        start += others_len
        self.ht = struct.unpack('?', str[start:start+1])[0]
        start += 1
        self.turbo = struct.unpack('?', str[start:start+1])[0]


'''
machine.fromString('13s13s5s5s2s3s??', machine.toString())
'''
