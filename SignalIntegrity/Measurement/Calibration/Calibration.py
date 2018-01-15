'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
from SignalIntegrity.Measurement.Calibration.ErrorTerms import ErrorTerms
from SignalIntegrity.SParameters.SParameters import SParameters
from numpy import hstack,vstack,matrix

class Calibration(object):
    FillInTransferThru=True
    def __init__(self,ports,f,calibrationList=[]):
        self.ports=ports
        self.f=f
        self.ET=None
        self.calibrationMatrix=[[[] for _ in range(self.ports)]
                                for _ in range(self.ports)]
        self.AddMeasurements(calibrationList)
    def __getitem__(self,item):
        return self.ET[item]
    def __len__(self):
        return len(self.f)
    def Fixtures(self):
        self.CalculateErrorTerms()
        return [SParameters(self.f,[
                vstack((hstack((matrix(self[n].Fixture(p)[0][0]),
                                matrix(self[n].Fixture(p)[0][1]))),
                        hstack((matrix(self[n].Fixture(p)[1][0]),
                                matrix(self[n].Fixture(p)[1][1]))))).tolist()
                    for n in range(len(self))]) for p in range(self.ports)]
    def WriteToFile(self,filename):
        Fixture=self.Fixtures()
        for p in range(self.ports):
            Fixture[p].WriteToFile(filename+str(p+1))
        return self
    def AddMeasurements(self,calibrationList=[]):
        self.ET=None
        for calibrationMeasurement in calibrationList:
            if calibrationMeasurement.type=='reflect':
                portDriven=calibrationMeasurement.port
                otherPort=portDriven
                self.calibrationMatrix[otherPort][portDriven].\
                    append(calibrationMeasurement)
            elif (calibrationMeasurement.type=='thru') or\
                (calibrationMeasurement.type=='xtalk'):
                portDriven=calibrationMeasurement.portDriven
                otherPort=calibrationMeasurement.otherPort
                self.calibrationMatrix[otherPort][portDriven].\
                    append(calibrationMeasurement)
        return self
    def CalculateErrorTerms(self,force=False):
        if (not self.ET is None) and (not force):
            return self
        self.ET=[ErrorTerms().Initialize(self.ports) for _ in range(len(self))]
        for port in range(self.ports):
            measurementList=self.calibrationMatrix[port][port]
            for n in range(len(self)):
                hatGamma=[measurement.gamma[n] for measurement in measurementList]
                Gamma=[measurement.Gamma[n][0][0] for measurement in measurementList]
                self[n].ReflectCalibration(hatGamma,Gamma,port)
        for otherPort in range(self.ports):
            for drivenPort in range(self.ports):
                if (otherPort != drivenPort):
                    measurementList=self.calibrationMatrix[otherPort][drivenPort]
                    xtalkMeasurementList=[]
                    thruMeasurementList=[]
                    for meas in measurementList:
                        if meas.type=='xtalk':
                            xtalkMeasurementList.append(meas)
                        elif meas.type=='thru':
                            thruMeasurementList.append(meas)
                    if len(xtalkMeasurementList)!=0:
                        for n in range(len(self.f)):
                            self[n].ExCalibration(xtalkMeasurementList[0].b2a1[n],
                                    otherPort,drivenPort)
                    if len(thruMeasurementList)!=0:
                        for n in range(len(self.f)):
                            b1a1=[measurement.b1a1[n]
                                  for measurement in thruMeasurementList]
                            b2a1=[measurement.b2a1[n]
                                  for measurement in thruMeasurementList]
                            S=[measurement.S[n] for measurement in thruMeasurementList]
                            self[n].ThruCalibration(b1a1,b2a1,S,otherPort,drivenPort)
        if Calibration.FillInTransferThru:
            for n in range(len(self.f)):
                self[n].TransferThruCalibration()
        return self
    def DutCalculation(self,sRaw):
        self.CalculateErrorTerms()
        return SParameters(self.f,[self[n].DutCalculation(sRaw[n])
                                   for n in range(len(self))])
