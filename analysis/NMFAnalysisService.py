import numpy 
import os
import sys
import traceback
import json
import threading
rootpath = os.path.dirname(os.path.realpath(sys.path[0]))
if not rootpath in sys.path:
        sys.path.append(rootpath)
from clusterService.ResultAdapter import *
from clusterService.ResultModel import NMFAnalysisResult

class AnalysisServiceConfig(object):
        def __init__(self):
                self.root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        def getInputPath(self):pass

        def getOutputPath(self):pass

class NMFAnalysisServiceConfig(AnalysisServiceConfig):
        def __init__(self):
                super(NMFAnalysisServiceConfig, self).__init__()
                self.inputRPath = ''
                self.outputRPath = ''

        def getInputPath(self):
                tmp = self.root_path + '/AllSource/ServerOutputService/' + self.inputRPath + '/Final'
                return tmp

        def getOutputPath(self):
                tmp = self.root_path + '/AllSource/ServerOutputService/' + self.outputRPath + '/ServerFinal'
                if not os.path.exists(tmp):
                        os.makedirs(tmp)
                return tmp + '/report.dat'
        
class NMFAnalysisService(threading.Thread):

        def __init__(self, config=NMFAnalysisServiceConfig()):
                super(NMFAnalysisService, self).__init__()
                self.config = config

        def difcost(self, a, b):
                dif=0
                for i in range(numpy.shape(a)[0]):
                        for j in range(numpy.shape(a)[1]):
                                # Euclidean Distance
                                dif+=pow(a[i,j]-b[i,j],2)
                return dif

        def factorize(self, v, pc=10, iter=10000):
                ic=numpy.shape(v)[0]
                fc=numpy.shape(v)[1]

                # Initialize the weight and feature matrices with random values
                w=numpy.matrix([[numpy.random.random() for j in range(pc)] for i in range(ic)])
                h=numpy.matrix([[numpy.random.random() for i in range(fc)] for i in range(pc)])

                # Perform operation a maximum of iter times
                etha = 1.0e-15 
                for i in range(iter):
                        wh=w*h
    
                        # Calculate the current difference
                        cost=self.difcost(v,wh)
    
                        #if i%10==0: print cost
    
                        # Terminate if the matrix has been fully factorized
                        if cost==0: 
                                print 'COST = ', cost
                                break
    
                        # Update feature matrix
                        hn=(numpy.transpose(w)*v)
                        hd=(numpy.transpose(w)*w*h)
                
                        h=numpy.matrix(numpy.array(h)*numpy.array(hn)/(numpy.array(hd)+etha))

                        # Update weights matrix
                        wn=(v*numpy.transpose(h))
                        wd=(w*h*numpy.transpose(h))
                
                        w=numpy.matrix(numpy.array(w)*numpy.array(wn)/(numpy.array(wd)+etha))
                print 'FINAL COST = ', cost
                return w,h, cost

        def reFactorize(self, data, pc=4, iter=10000):
                minCost = 99999999
                minW = None
                minH = None
                for i in range(3):
                        w, h, cost = self.factorize(numpy.matrix(data), pc=pc, iter=iter)
                        if cost<minCost:
                                minW = w
                                minH = h
                                minCost = cost
                print 'MIN COST = ', minCost
                return minW, minH

        def scaledata(self, datas, metrics):
                low = [999999999.0]*len(datas[0])
                high = [-999999999.0]*len(datas[0])
                for row in datas:
                        for i in range(len(row)):
                                if row[i]<low[i]: low[i] = row[i]
                                if row[i]>high[i]: high[i] = row[i]
                divid = [1.0]*len(datas[0])
                for i in range(len(high)):
                        if not high[i]:
                                divid[i] = -1
                        elif float(high[i]-low[i])/float(high[i])<0.1:
                                divid[i] = -1
                        else:
                                if not high[i] > 0: continue
                                if high[i] > 1:
                                        tmp = high[i]
                                        while tmp > 1:
                                                divid[i] *= 10
                                                tmp /= 10
                                elif high[i] < 0.1:
                                        tmp = high[i]
                                        while tmp < 0.1:
                                                divid[i] /= 10
                                                tmp *= 10

                newDatas = []
                newMetrics = []
                newRawDatas = []

                rc = len(datas)
                for i in range(rc):
                        newDatas.append([])
                        newRawDatas.append([])

                for i in range(len(datas[0])):
                        if not divid[i] == -1:
                                for j in range(len(datas)):
                                        try:
                                                newDatas[j].append(datas[j][i]/divid[i])
                                        except:
                                                newDatas[j].append(0)
                                        newRawDatas[j].append(datas[j][i])
                                newMetrics.append(metrics[i])

                return newDatas, newRawDatas, newMetrics

        def scaleDataByMaxValue(self, datas):
                tmpMaxs = []
                for row in datas:
                        tmpMaxs.append(max(row))
                maxValue = max(tmpMaxs)

                divid = 1
                if maxValue > 0:
                        if maxValue > 1:
                                while maxValue > 1:
                                        divid *= 10
                                        maxValue /= 10
                        elif maxValue < 0.1:
                                while maxValue < 0.1:
                                        divid /= 10
                                        maxValue *= 10

                newDatas = []
                for row in datas:
                        tmp = []
                        for i in range(len(row)):
                                try:
                                        tmp.append(row[i]/divid)
                                except:
                                        tmp.append(0)
                        newDatas.append(tmp)
                return newDatas

        def readAndAnalysisDatas(self):
                print 'NMF SERVICE'
                realPath = self.config.getInputPath()
                rawDatas ,rawMetricNames ,allTestNames = ResultAdapter().getNMFAnalysisServiceInputs(self.config.inputRPath)
                newDatas, newRawDatas, newMetrics = self.scaledata(rawDatas, rawMetricNames)
                print 'NUMBER OF NEWMETRICS : ', len(newMetrics)
                weights, features = self.reFactorize(newDatas, pc=self.featuresCount)
                self.outputDatas(weights, features, newMetrics, allTestNames, newDatas, newRawDatas)
                print 'NMF SERVICE DONE'
                return True

        def outputDatas(self, weights, features, metricNames, testNames, testDatas, rawTestDatas):
                fc, mc = numpy.shape(features)
                outputMetrics = []
                for i in range(fc):
                        feature = []
                        for j in range(mc):
                                feature.append(features[i, j])
                        for j in range(3):
                                value = max(feature)
                                index = feature.index(value)
                                if not metricNames[index] in outputMetrics: 
                                        outputMetrics.append(metricNames[index])
                                feature[index] = -1
                outputMetrics.sort()
                
                outputFeatures = []
                for i in range(fc):
                        outputFeatures.append(['feature'+str(i+1), []])
                        outputFeatures.append(['value'+str(i+1), []])
                for i in range(fc):
                        feature = []
                        for j in range(mc):
                                feature.append(features[i, j])
                        for j in range(10):
                                value = max(feature)
                                index = feature.index(value)
                                outputFeatures[2*i][1].append(metricNames[index])
                                outputFeatures[2*i+1][1].append(value)
                                feature[index] = -1

                outputTests = []
                outputRawTests = []
                outputTestFeatures = []
                tc, tfc = numpy.shape(weights)
                for i in range(tc):
                        tmp = []
                        rawTmp = []
                        for metric in outputMetrics:
                                j = metricNames.index(metric)
                                tmp.append(testDatas[i][j])
                                rawTmp.append(rawTestDatas[i][j])
                        tmpFeatures = []
                        for j in range(tfc):
                                tmpFeatures.append(weights[i, j])
                        value = max(tmpFeatures)
                        index = tmpFeatures.index(value)
                        outputTestFeatures.append([testNames[i], index+1])
                        outputRawTests.append([testNames[i], rawTmp])
                        outputTests.append([testNames[i], tmp])
                fileName = self.config.getOutputPath()
                nMFResult = NMFAnalysisResult('nmf analysis result', fileName)
                nMFResult.testBelongFeatures = outputTestFeatures
                nMFResult.featureMetrics = outputMetrics
                nMFResult.featureClasses = outputFeatures
                nMFResult.formatTestsDatas = outputTests
                nMFResult.rawTestsDatas = outputRawTests
                outputFile = file(fileName, 'w')
                outputFile.write(nMFResult.dumps())
                outputFile.close()        

        def setParameters(self, inputRPath, outputRPath, featuresCount):
                self.config.inputRPath = inputRPath
                self.config.outputRPath = outputRPath      
                self.featuresCount = featuresCount

        def run(self):
                self.readAndAnalysisDatas()

def main():
        analysis = NMFAnalysisService()
        analysis.setParameters('serviceresult', 5)
        analysis.start()
        print 'done'

if __name__ == '__main__':
        main()
