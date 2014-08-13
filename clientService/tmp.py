class Job(object):
    '''
        pid: -1 platform
        path: relative path
        source_path : relative source path
        pmu_paras: dict {
            duration: int
            loops: int
            delay: int
        }
        sar_paras: dict{
            interval: int
            loops: int
        }
        hotspots_paras: dict{
            duration: int
        }
        perf_list_paras: dict {
            'duration': int
            'delay': int
        }
    '''
    def __init__(self, path, pid, sar_paras=None, pmu_paras=None, hotspots_paras=None, perf_list_paras=None, rmon_paras=None):
        self.path = path
        self.pid = pid
        self.sar_paras = sar_paras
        self.pmu_paras = pmu_paras
        self.hotspots_paras = hotspots_paras
        self.perf_list_paras = perf_list_paras
        self.rmon_paras = rmon_paras
