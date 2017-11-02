'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
from numpy import matrix
from numpy.linalg import det

from SignalIntegrity.SParameters.SParameters import SParameters
from SignalIntegrity.Conversions.S2T import S2T
from SignalIntegrity.Conversions.T2S import T2S

class CalibrationMeasurement(object):
    def __init__(self,type,name=None):
        self.type=type
        self.name=name

class ReflectCalibrationMeasurement(CalibrationMeasurement):
    # gamma is the raw measurement, Gamma is the known value of the standard
    def __init__(self,gamma,Gamma,port,name=None):
        CalibrationMeasurement.__init__(self,'reflect',name)
        self.gamma=gamma
        self.Gamma=Gamma
        self.port = port

class ThruCalibrationMeasurement(CalibrationMeasurement):
    def __init__(self,s,S,portDriven,otherPort,name=None):
        CalibrationMeasurement.__init__(self,'thru',name)
        self.s=s
        self.S=S
        self.portDriven=portDriven
        self.otherPort=otherPort

class CalibrationMeasurements(object):
    def __init__(self,ports,calibrationList=[]):
        self.ports=ports
        self.ET=None
        self.calibrationMatrix=[[[] for _ in range(self.ports)] for _ in range(self.ports)]
        self.AddMeasurements(calibrationList)
    def AddMeasurements(self,calibrationList=[]):
        self.ET=None
        for calibrationMeasurement in calibrationList:
            if calibrationMeasurement.type=='reflect':
                portDriven=calibrationMeasurement.port
                otherPort=portDriven
                self.calibrationMatrix[otherPort-1][portDriven-1].append(calibrationMeasurement)
            elif calibrationMeasurement.type=='thru':
                portDriven=calibrationMeasurement.portDriven
                otherPort=calibrationMeasurement.otherPort
                self.calibrationMatrix[otherPort-1][portDriven-1].append(calibrationMeasurement)
        return self
    def CalculateErrorTerms(self):
        self.ET=[[None for _ in range(self.ports)] for _ in range(self.ports)]
        for port in range(self.ports):
            measurementList=self.calibrationMatrix[port][port]
            self.ET[port][port]=self.CalculateReflectErrorTerms(measurementList)
        for otherPort in range(self.ports):
            for drivenPort in range(self.ports):
                measurementList=self.calibrationMatrix[otherPort][drivenPort]
                if otherPort==drivenPort:
                    pass
                else:
                    self.ET[otherPort][drivenPort]=\
                        self.CalculateThruErrorTerms(measurementList,self.ET[drivenPort][drivenPort])
        return self
    def CalculateReflectErrorTerms(self,measurementList):
        fList=measurementList[0].gamma.m_f
        data=[]
        for n in range(len(fList)):
            left=[[0. for _ in range(3)] for _ in range(len(measurementList))]
            right=[[0.] for _ in range(len(measurementList))]
            for m in range(len(measurementList)):
                left[m][0]=1.
                left[m][1]=measurementList[m].Gamma[n][0][0]*measurementList[m].gamma[n][0][0]
                left[m][2]=-measurementList[m].Gamma[n][0][0]
                right[m]=[measurementList[m].gamma[n][0][0]]
            (Ed,Es,detS)=tuple((matrix(left).getI()*matrix(right)).tolist())
            Er=detS-Ed*Es
            data.append([[Ed,1.],[Er,Es]])
        return SParameters(fList,data)
    def CalculateThruErrorTerms(self,measurementList,reflectErrorTerms):
        self.ET=None
        fList=measurementList[0].s.m_f
        data=[]
        for n in range(len(fList)):
            leftEl=[[0.] for _ in range(len(measurementList))]
            rightEl=[[0.] for _ in range(len(measurementList))]
            for m in range(len(measurementList)):
                S=measurementList[m].S[n]
                s=measurementList[m].s[n]
                SL=T2S(S2T(reflectErrorTerms[n])*S2T(S))
                detSL=det(matrix(SL)).tolist()
                leftEl[m][0]=detSL-s[0][0]*s[1][1]
                rightEl[m][0]=SL[0][0]-s[0][0]
            El=(matrix(leftEl).getI()*matrix(rightEl)).tolist()[0][0]
            leftEt=[[0.] for _ in range(len(measurementList))]
            rightEt=[[0.] for _ in range(len(measurementList))]
            for m in range(len(measurementList)):
                S=measurementList[m].S[n]
                s=measurementList[m].s[n]
                SL=T2S(S2T(reflectErrorTerms[n])*S2T(S))
                detSL=det(matrix(SL)).tolist()
                leftEt[m][0]=SL[1][0]
                rightEt[m][0]=s[1][0]*(1-SL[1][1]*El)
            Et=(matrix(leftEt).getI()*matrix(rightEt)).tolist()[0][0]
            data.append([[El,0.],[Et,0.]])
        return SParameters(fList,data)
    def ErrorTerms(self):
        if self.ET is None:
            self.CalculateErrorTerms()
        return self.ET
