"""
Calibration
"""

# Copyright (c) 2018 Teledyne LeCroy, Inc.
# All rights reserved worldwide.
#
# This file is part of SignalIntegrity.
#
# SignalIntegrity is free software: You can redistribute it and/or modify it under the terms
# of the GNU General Public License as published by the Free Software Foundation, either
# version 3 of the License, or any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <https://www.gnu.org/licenses/>

from SignalIntegrity.Lib.Measurement.Calibration.ErrorTerms import ErrorTerms
from SignalIntegrity.Lib.SParameters.SParameters import SParameters
from numpy import hstack,vstack,matrix

class Calibration(object):
    """Generates calibrated s-parameter measurements"""
    FillInTransferThru=True
    def __init__(self,ports,f,calibrationList=[]):
        """Constructor
        @param ports number of ports in the calibration.
        @param f instance of class FrequencyList (or list of frequencies).
        @param calibrationList (optional) list of instances of class CalibrationMeasurement
        @see CalibrationMeasurement
        """
        self.ports=ports
        self.f=f
        self.ET=None
        self.calibrationMatrix=[[[] for _ in range(self.ports)]
                                for _ in range(self.ports)]
        self.AddMeasurements(calibrationList)
    def __getitem__(self,item): return self.ET[item]
    """overloads [item]
    @param item integer row of error terms matrix to access
    @return a row of the error terms matrix
    @remark
    This method is used when access the error terms matrix like self[r][c] which
    would acess an instance of class ErrorTerms for receive port r and driven port c.
    @see ErrorTerms
    """
    def __len__(self): return len(self.f)
    """overloads len()
    @return the number of rows in the error terms (which is the number of ports).
    """
    def Fixtures(self):
        """Fixtures
        @return the error terms as fixtures
        """
        self.CalculateErrorTerms()
        return [SParameters(self.f,[
                vstack((hstack((matrix(self[n].Fixture(p)[0][0]),
                                matrix(self[n].Fixture(p)[0][1]))),
                        hstack((matrix(self[n].Fixture(p)[1][0]),
                                matrix(self[n].Fixture(p)[1][1]))))).tolist()
                    for n in range(len(self))]) for p in range(self.ports)]
    def WriteToFile(self,filename):
        """Writes the error terms to a file
        @param filename name of the file to write the error terms to.
        """
        Fixture=self.Fixtures()
        for p in range(self.ports):
            Fixture[p].WriteToFile(filename+str(p+1))
        return self
    def AddMeasurements(self,calibrationList=[]):
        """Adds calibration measurements
        @param calibrationList list of instances of class CalibrationMeasurement.
        """
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
        """Calculates the error terms
        @param force (optional) boolean whether to force it to calculate the error terms.
        @remark
        If error terms have not been calculated or force, then the error terms are calculated
        from instances of CalibrationMeasurement provided during the calibration."""
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
        """calculates the Dut.\n
        converts the raw measured s-parameters of the DUT into calibrated s-parameter
        measurements.
        @param sRaw instance of class SParameters of the raw measurement of the DUT.
        @return instance of class SParameters of the calibrated DUT measurement.
        """
        self.CalculateErrorTerms()
        return SParameters(self.f,[self[n].DutCalculation(sRaw[n])
                                   for n in range(len(self))])
