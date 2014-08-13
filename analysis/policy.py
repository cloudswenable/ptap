import os
from xml.etree import ElementTree

class Policy(object):

    def __init__(self, name=None, realMetric=None, summary=None, threshold_min=None, threshold_max=None, bigger_better=False, suggestion=None, type=None):
        self.name = name
        self.realMetric = realMetric
        self.formula = None
        self.parameters = None
        self.summary = summary
        self.threshold_min = threshold_min
        self.threshold_max = threshold_max
        self.bigger_better = bigger_better
        self.suggestion = suggestion
        self.type = type

    def getSuggestion(self, value):
        if not value: return self.suggestion
        value = float(value)
        eval = self.evaluate(value)
        if eval == 1:
                return 'good'
        elif eval == 0:
                return 'normal'
        else:
                return self.suggestion
        
    def evaluate(self, value):
        '''
            evaluate current metric is better or not
            return: 1 : good,  0: normal, -1: bad
        '''
        ret = None
        if value >= self.threshold_min and value <= self.threshold_max:
            ret = 0
        elif value > self.threshold_max:
            ret = -1
        else:
            ret = 1

        if self.bigger_better:
            ret = -(ret)
        return ret


class PolicyManager(object):

    def __init__(self, conf_file='/config/policy.xml'):
        self.conf_file = os.path.dirname(__file__) + conf_file
        self.policys = {}
        self.constructPolicys()

    def constructPolicys(self):
        policy_tree = ElementTree.parse(self.conf_file)
        policy_root = policy_tree.getroot()

        for child in  policy_root:
            policy = Policy()
            for element in child.iter():
                if element.tag == 'metric':
                    policy.name = element.text
                if element.tag == 'min':
                    policy.threshold_min = float(element.text)
                if element.tag == 'max':
                    policy.threshold_max = float(element.text)
                if element.tag == 'bettervalue':
                    if element.text == 'smaller':
                        policy.bigger_better = False
                    else:
                        policy.bigger_better = True
                if element.tag == 'suggestion':
                    policy.suggestion = element.text.strip()
                if element.tag == 'type':
                    policy.type = element.text
                if element.tag == 'summary':
                    policy.summary = element.text
                if element.tag == 'realMetric':
                    policy.realMetric = element.text
                if element.tag == 'formula':
                    policy.formula = element.text
                if element.tag == 'parameters':
                    ps = []
                    for celement in element.iter():
                        if celement.tag == 'p':
                                ps.append(celement.text)
                    policy.parameters = ps
            self.policys[policy.name.lower()] = policy
        #print self.policys

    def getPolicy(self, policy_name):
        policy = self.policys.get(policy_name, None)
        return policy



#manager = PolicyManager()
#manager.constructPolicys()


