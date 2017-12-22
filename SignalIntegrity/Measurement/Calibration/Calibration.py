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

class Calibration(object):
    def __init__(self,ports,f,calibrationList=[]):
        self.ports=ports
        self.f=f
        self.ET=[ErrorTerms().Initialize(ports) for _ in range(len(self.f))]
        self.calibrationMatrix=[[[] for _ in range(self.ports)]
                                for _ in range(self.ports)]
        self.AddMeasurements(calibrationList)
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
    def CalculateErrorTerms(self):
        self.ET=[ErrorTerms().Initialize(self.ports) for _ in range(len(self.f))]
        for port in range(self.ports):
            measurementList=self.calibrationMatrix[port][port]
            for n in range(len(self.f)):
                hatGamma=[measurement.gamma[n] for measurement in measurementList]
                Gamma=[measurement.Gamma[n][0][0] for measurement in measurementList]
                self.ET[n].ReflectCalibration(hatGamma,Gamma,port)
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
                            self.ET[n].ExCalibration(xtalkMeasurementList[0].b2a1[n],
                                    otherPort,drivenPort)
                    if len(thruMeasurementList)!=0:
                        for n in range(len(self.f)):
                            b1a1=[measurement.b1a1[n]
                                  for measurement in thruMeasurementList]
                            b2a1=[measurement.b2a1[n]
                                  for measurement in thruMeasurementList]
                            S=[measurement.S[n] for measurement in thruMeasurementList]
                            self.ET[n].ThruCalibration(b1a1,b2a1,S,otherPort,drivenPort)
        for otherPort in range(self.ports):
            for drivenPort in range(self.ports):
                if (otherPort != drivenPort):
                    if all(self.ET[0][otherPort][drivenPort][1:])==0.:
                        # print 'need to compute thru'+str(otherPort+1)+str(drivenPort+1)
                        for mid in range(self.ports):
                            if all(self.ET[0][otherPort][drivenPort][1:])==0.:
                                if ((mid != otherPort) and
                                    (mid != drivenPort) and
                                    (any(self.ET[0][otherPort][mid][1:])!=0.) and
                                    (any(self.ET[0][mid][drivenPort][1:])!=0.)):
                                    # print 'did it with '+str(otherPort+1)+str(mid+1)+' and '+str(mid+1)+str(drivenPort+1)
                                    for n in range(len(self.f)):
                                        (Exl,Etl,Ell)=self.ET[n][otherPort][mid]
                                        (Exr,Etr,Elr)=self.ET[n][mid][drivenPort]
                                        (Edm,Erm,Esm)=self.ET[n][mid][mid]
                                        (Edo,Ero,Eso)=self.ET[n][otherPort][otherPort]
                                        (Ex,Et,El)=self.ET[n][otherPort][drivenPort]
                                        Et=Etl*Etr/Erm
                                        El=Eso
                                        self.ET[n][otherPort][drivenPort]=[Ex,Et,El]
        return self
    def ErrorTerms(self):
        if self.ET is None:
            self.CalculateErrorTerms()
        return self.ET
    def DutCalculation(self,sRaw):
        self.ErrorTerms()
        return SParameters(self.f,[self.ET[n].DutCalculation(sRaw[n])
                                   for n in range(len(self.f))])
