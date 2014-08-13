from MetricsManager import MetricsManager, MetricsManagerConfig

class PerfListMetricsManagerConfig(MetricsManagerConfig):
        def __init__(self):
                MetricsManagerConfig.__init__(self)
                self.eventsFile = self.config.get('metricsManager', 'PerfListMetricsManager_events_file')
                self.metricsFile = self.config.get('metricsManager', 'PerfListMetricsManager_metrics_file')

class PerfListMetricsManager(MetricsManager):
    def __init__(self, config=PerfListMetricsManagerConfig()):
        MetricsManager.__init__(self, config)
        self.events = self.parseEvents()
        self.eventsNickNames, self.metrics = self.parseMetrics()

    def parseEvents(self):
        events = []
        for line in open(self.eventsFile, 'r'):
              events.append(line.strip())
        return events

    def parseMetrics(self):
        metrics = []
        nickName = []
        for line in open(self.metricsFile, 'r'):
            items = line.split('#')
            nickName.append(items[0].strip())
            metrics.append(items[1].strip())
        return nickName, metrics

    def getAllEvents(self):
        tmpEventStr = ','.join(self.events)
        return tmpEventStr

    def getEvents(self):
        return self.events

    def getMetrics(self):
        return self.metrics

def main():
        manager = PerfListMetricsManager()
        print manager.getMetrics()

if __name__ == '__main__':
        main()
