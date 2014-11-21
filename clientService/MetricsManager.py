import os
import ConfigParser
from xml.etree import ElementTree

class MetricsManagerConfig(object):
        def __init__(self):
                self.basePath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                self.config = ConfigParser.ConfigParser()
                confFile = open(self.basePath + '/clientService/config/metricsConfig.cfg', 'r')
                self.config.readfp(confFile)

        def getEventsFilePath(self):
                return self.basePath + self.eventsFile

        def getMetricsFilePath(self):
                return self.basePath + self.metricsFile

class MetricsManager:
    def __init__(self, config):
        self.eventsFile = config.getEventsFilePath()
        self.metricsFile = config.getMetricsFilePath()

COLON = 'colon'
EQUAL = 'equal'

def translateEventName(eventName):
    return eventName.replace(':', COLON).replace('=', EQUAL)

class Event:
    def __init__(
        self,
        realName=None,
        reportName=None,
        configs=None,
        ):
        self.realName = realName
        self.reportName = reportName
        self.configs = configs

    def getEvent(self):
        string = 'cpu/'
        for i in range(len(self.configs)):
            if i != 0:
                string += 'config' + str(i) + '='
                string += self.configs[i] + ','
            else:
                string += 'config='
                string += self.configs[0] + ','
        string += 'name=' + self.reportName + '/'
        return string

    def getRawEvent(self):
        return 'r'+self.configs[0][2:]

class Metric:

    def __init__(
        self,
        name,
        eventsDict,
        constantDict,
        formula,
        thMeName=None,
        ):
        self.name = name
        self.eventsDict = eventsDict
        self.constantDict = constantDict
        self.formula = formula
        self.thMeName = thMeName

    def getEvents(self):
        return self.eventsDict.values()

    def getConstants(self):
        return self.constantDict.values()

    def getAliasEventDict(self):
        return self.eventsDict

    def getAliasConstantDict(self):
        return self.constantDict

    def getAliasEvent(self, alias):
        return self.eventsDict.get(alias)

    def getAliasConstant(self, alias):
        return self.constantDict.get(alias)

    def getFormula(self):
        return self.formula

    def getString(self):
        tmpstring = self.name + str(self.eventsDict) \
            + str(self.constantDict) + self.formula + str(self.thMeName)
        return tmpstring

class XMLParser:

    def __init__(self, configFile, elementTag):
        self.configFile = configFile
        self.elementTag = elementTag

    def getElements(self):
        configStr = open(self.configFile, 'r').read()
        root = ElementTree.fromstring(configStr)
        rawElements = root.getiterator(self.elementTag)
        self.elements = {}
        for rawElement in rawElements:
            (name, element) = self.getElement(rawElement)
            self.elements[name] = element
        return self.elements

class EventsParser(XMLParser):

    def __init__(
        self,
        configFile='../eventsConfig/events.xml',
        eventTag='event',
        realNameTag='realName',
        configsTag='configs',
        configTag='config',
        ):
        XMLParser.__init__(self, configFile, eventTag)
        self.realNameTag = realNameTag
        self.configsTag = configsTag
        self.configTag = configTag

    def getElement(self, rawElement):
        name = rawElement.getiterator(self.realNameTag)[0].text
        rawConfigs = \
            rawElement.getiterator(self.configsTag)[0].getiterator(self.configTag)
        configs = []
        for config in rawConfigs:
            configs.append(config.text)
        return (translateEventName(name), Event(name,
                translateEventName(name), configs))

    def getEvents(self):
        events = []
        events_tree = ElementTree.parse(self.configFile)
        events_root = events_tree.getroot()
        for child_of_root in events_root:
            event = Event()
            for element in child_of_root.iter():
                if element.tag == 'realName':
                    event.realName = element.text
                    event.reportName = translateEventName(event.realName)
                if element.tag == 'config':
                    event.configs.append(element.text)
            events.append(event)
        return events

class MetricsParser(XMLParser):

    def __init__(
        self,
        configFile='../eventsConfig/snb-ep.xml',
        metricTag='metric',
        nameTag='name',
        eventTag='event',
        aliasTag='alias',
        constantTag='constant',
        formulaTag='formula',
        thMeNameTag='throughput-metric-name',
        ):
        XMLParser.__init__(self, configFile, metricTag)
        self.nameTag = nameTag
        self.eventTag = eventTag
        self.aliasTag = aliasTag
        self.constantTag = constantTag
        self.formulaTag = formulaTag
        self.thMeNameTag = thMeNameTag

    def getElement(self, rawElement):
        name = rawElement.attrib[self.nameTag]
        rawEvents = rawElement.getiterator(self.eventTag)
        events = {}
        for rawEvent in rawEvents:
            aliasName = rawEvent.attrib[self.aliasTag]
            eventName = rawEvent.text
            events[aliasName] = translateEventName(eventName)
        rawConstants = rawElement.getiterator(self.constantTag)
        constants = {}
        for rawConstant in rawConstants:
            aliasName = rawConstant.attrib[self.aliasTag]
            constantName = rawConstant.text
            constants[aliasName] = constantName
        formula = rawElement.getiterator(self.formulaTag)[0].text
        thMeNameList = rawElement.getiterator(self.thMeNameTag)
        thMeName = None
        if len(thMeNameList) > 0:
            thMeName = thMeNameList[0].text
        return (name, Metric(name, events, constants, formula,
                thMeName))


def main(): pass
if __name__ == '__main__':
    main()
