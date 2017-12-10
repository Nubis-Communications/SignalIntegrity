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

class XtalkCalibrationMeasurement(CalibrationMeasurement):
    def __init__(self,s,portDriven,otherPort,name=None):
        CalibrationMeasurement.__init__(self,'xtalk',name)
        self.s=s
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
            elif (calibrationMeasurement.type=='thru') or (calibrationMeasurement.type=='xtalk'):
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
            EdEsdetS=(matrix(left).getI()*matrix(right)).tolist()
            (Ed,Es,detS)=(EdEsdetS[0][0],EdEsdetS[1][0],EdEsdetS[2][0])
            Er=Ed*Es-detS
            data.append([[Ed,1.],[Er,Es]])
        return SParameters(fList,data)
    def CalculateThruErrorTerms(self,measurementList,reflectErrorTerms):
        xtalkMeasurementList=[]
        thruMeasurementList=[]
        for meas in measurementList:
            if meas.type=='xtalk':
                xtalkMeasurementList.append(meas)
            elif meas.type=='thru':
                thruMeasurementList.append(meas)
        if len(xtalkMeasurementList)==0:
            ExSp=0
        else:
            ExSp=xtalkMeasurementList[0].s
        fList=thruMeasurementList[0].s.m_f
        data=[]
        for n in range(len(fList)):
            A=[[0. for _ in range(2)] for _ in range(2*len(thruMeasurementList))]
            B=[[0.] for _ in range(2*len(thruMeasurementList))]
            Ed=reflectErrorTerms[n][0][0]
            Er=reflectErrorTerms[n][1][0]
            Es=reflectErrorTerms[n][1][1]
            Ex=ExSp[n]
            for m in range(len(thruMeasurementList)):
                S=thruMeasurementList[m].S[n]
                s=thruMeasurementList[m].s[n]
                detS=det(matrix(S))
                A[2*m][0]=(Es*detS-S[1][1])*(Ed-s[0][0])-Er*detS
                A[2*m][1]=0.
                A[2*m+1][0]=(Es*detS*S[1][1])*(Ex-s[1][0])
                A[2*m+1][1]=s[1][0]
                B[2*m][0]=(1.-Es*S[0][0])*(s[0][0]-Ed)-Er*s[0][0]
                B[2*m+1][0](1.-Es*S[0][0])*(s[1][0]-Ex)
            ElEt=(matrix(B)*matrix(A).getI()).tolist()
            (El,Et)=(ElEt[0][0],ElEt[1][0])
            data.append([[El,Ex],[Et,0.]])
        return SParameters(fList,data)
    def ErrorTerms(self):
        if self.ET is None:
            self.CalculateErrorTerms()
        return self.ET
