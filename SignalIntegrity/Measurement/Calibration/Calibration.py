"""
Calibration
"""
# Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
# Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
# All Rights Reserved.
# 
# Explicit license in accompanying README.txt file.  If you don't have that file
# or do not agree to the terms in that file, then you are not licensed to use
# this material whatsoever.

from SignalIntegrity.Measurement.Calibration.ErrorTerms import ErrorTerms
from SignalIntegrity.SParameters.SParameters import SParameters
from numpy import hstack,vstack,matrix

## Calibration
#
# This class generates calibrated s-parameter measurements
#
class Calibration(object):
    FillInTransferThru=True
    ## Constructor
    #
    # @param ports number of ports in the calibration.
    # @param f instance of class FrequencyList (or list of frequencies).
    # @param calibrationList (optional) list of instances of class CalibrationMeasurement
    #
    # @see CalibrationMeasurement
    #
    def __init__(self,ports,f,calibrationList=[]):
        self.ports=ports
        self.f=f
        self.ET=None
        self.calibrationMatrix=[[[] for _ in range(self.ports)]
                                for _ in range(self.ports)]
        self.AddMeasurements(calibrationList)
    ## overloads [item]
    #
    # @param item integer row of error terms matrix to access
    # @return a row of the error terms matrix
    #
    # This method is used when access the error terms matrix like self[r][c] which
    # would acess an instance of class ErrorTerms for receive port r and driven port c.
    #
    # @see ErrorTerms
    #
    def __getitem__(self,item):
        return self.ET[item]
    ## overloads len()
    #
    # @return the number of rows in the error terms (which is the number of ports).
    #
    def __len__(self):
        return len(self.f)
    ## Fixtures
    #
    # @return the error terms as fixtures
    #
    def Fixtures(self):
        self.CalculateErrorTerms()
        return [SParameters(self.f,[
                vstack((hstack((matrix(self[n].Fixture(p)[0][0]),
                                matrix(self[n].Fixture(p)[0][1]))),
                        hstack((matrix(self[n].Fixture(p)[1][0]),
                                matrix(self[n].Fixture(p)[1][1]))))).tolist()
                    for n in range(len(self))]) for p in range(self.ports)]
    ## WriteToFile
    #
    # @param filename name of the file to write the error terms to.
    #
    # Writes the error terms to a file
    #
    def WriteToFile(self,filename):
        Fixture=self.Fixtures()
        for p in range(self.ports):
            Fixture[p].WriteToFile(filename+str(p+1))
        return self
    ## AddMeasurments
    #
    # @param calibrationList list of instances of class CalibrationMeasurement
    #
    # Adds calibration measurements to the calibration.
    #
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
    ## CalculateErrorTerms
    #
    # @param force (optional) boolean whether to force it to calculate the error terms.
    #
    # If error terms have not been calculated or force, then the error terms are calculated
    # from instances of CalibrationMeasurement provided during the calibration.
    #
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
    ## DutCalculation
    #
    # @param sRaw instance of class SParameters of the raw measurement of the DUT.
    # @return instance of class SParameters of the calibrated DUT measurement.
    #
    # converts the raw measured s-parameters of the DUT into calibrated s-parameter
    # measurements. 
    def DutCalculation(self,sRaw):
        self.CalculateErrorTerms()
        return SParameters(self.f,[self[n].DutCalculation(sRaw[n])
                                   for n in range(len(self))])
