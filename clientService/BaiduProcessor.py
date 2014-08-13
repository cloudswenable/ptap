__author__ = 'jimmy'

from Processor import *
from Util import *

class BaiduProcessorConfig(ProcessorConfig):

    def __init__(self):
        super(BaiduProcessorConfig, self).__init__()
        self.rPath = ''

    def getInputFile(self):
        tmp = 'AllSource/ClientOutput/' + self.rPath + '/Raw/Metrics/RMON/report.dat'
        return self.root_path + '/' + tmp

    def getOutputPath(self):
        tmp = 'AllSource/ClientOutput/' + self.rPath + '/Process/Metrics/RMON/'
        path = createPaths(self.root_path, tmp) + 'report.dat'
        return path

class BaiduProcessor(Processor):

    def __init__(self, config=BaiduProcessorConfig()):
        super(BaiduProcessor, self).__init__()
        self.config = config

    def process(self, input_path, output_path):
        rmon_result = AppModelResult(name='rmon', path=output_path)
        cpu_datas = []
        memory_datas_read = []
        memory_datas_write = []
        io_datas_read = []
        io_datas_write = []
        net_datas_read = []
        net_datas_write = []
        power_datas_cpu = []
        power_datas_mem = []
        mem_usages =  []
        disk_usages = []

        for line in open(input_path):
            datas = line.split()
            if 'score' in line:
                # single core usage
                cpu_datas.append(float(datas[1][:-1]))
            elif '(io)' in line:
                # disk io
                io_datas_read.append(float(datas[1][:-4]))
                io_datas_write.append(float(datas[2][:-4]))
            elif '(net)' in line:
                # NIC io
                net_datas_read.append(float(datas[1][:-4]))
                net_datas_write.append(float(datas[2][:-4]))
            elif 'SALL' in line:
                # power cpu
                power_datas_cpu.append(float(datas[1]))
            elif 'MALL' in line:
                # power mem
                power_datas_mem.append(float(datas[1]))
            elif 'System Read Thr' in line:
                # memory read
                memory_datas_read.append(float(datas[3]))
            elif 'System Write Thr' in line:
                #memory write
                memory_datas_write.append(float(datas[3]))
            elif '(mem)' in line:
                mem_usages.append(datas[1])
            elif '(disk)' in line:
                disk_usages.append(datas[1])

        sum_net_read = 0.0
        sum_net_write = 0.0
        for n_read in net_datas_read:
            sum_net_read += n_read

        for n_write in net_datas_write:
            sum_net_write += n_write

        #NIC 1000Mb/s = 128000 KB/s
        #TODO check the nic bandwidth
        avg_net_read_usage = sum_net_read/len(net_datas_read)/128000
        avg_net_write_usage = sum_net_write/len(net_datas_write)/128000
        if avg_net_read_usage > avg_net_write_usage:
            rmon_result.net_usage = avg_net_read_usage
        else:
            rmon_result.net_usage = avg_net_write_usage

        sum_cpu_usage = 0.0
        for n_cpu in cpu_datas:
            sum_cpu_usage += n_cpu

        avg_cpu_usage = sum_cpu_usage/len(cpu_datas)
        rmon_result.cpu_usage = avg_cpu_usage

        #mem 64GB = 67108864KB
        #TODO check the current mem volume
        mem_usage = mem_usages[-1]
        mem_usage_percent = float(mem_usage[0:-4])/67108864
        rmon_result.mem_usage = mem_usage_percent

        #disk 1TB = 1073741824KB
        #TODO check the util%
        rmon_result.disk_usage = float(disk_usages[-1][0:-4])/1073741824

        rmon_result.cpuDatas = [cpu_datas]
        rmon_result.ioUtilDatas = [io_datas_read, io_datas_write]
        rmon_result.memBandwidthDatas = [memory_datas_read, memory_datas_write]
        rmon_result.netBandwidthDatas = [net_datas_read, net_datas_write]
        rmon_result.powerDatas = [power_datas_cpu, power_datas_mem]
        return [rmon_result]

    def handle(self, job):
        self.config.rPath = job.path
        input_path = self.config.getInputFile()
        output_path = self.config.getOutputPath()
        return self.process(input_path, output_path)
