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
from SignalIntegrity.Lib.FrequencyDomain.FrequencyList import EvenlySpacedFrequencyList
from SignalIntegrity.Lib.SystemDescriptions.SystemSParametersNumeric import SystemSParametersNumeric
from SignalIntegrity.Lib.Measurement.Calibration.CalibrationMeasurements import ThruCalibrationMeasurement
from SignalIntegrity.Lib.Devices.Thru import Thru
import sys
import copy

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
    def InitializeFromFixtures(self,fixtureList):
        """initializes the calibration from list of fixtures
        @param fixtureList list of instances of class SParameters

        For a given number of ports P, there should be P fixtures in the list
        and each fixture should be 2P port s-parameters
        """
        self.ports=len(fixtureList)
        self.f=fixtureList[0].m_f
        self.calibrationMatrix=[[[] for _ in range(self.ports)]
                                for _ in range(self.ports)]
        self.ET=[ErrorTerms().InitializeFromFixtures([fixture[n]
                for fixture in fixtureList]) for n in range(len(self))]
        return self
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
    def Fixtures(self,pl=None):
        """Fixtures
        @return the error terms as fixtures
        @param pl (optional) list of zero based port numbers of the DUT

        @remark If the portList is None, then it assumed to be a list [0,1,2,P-1] where P is the
        number of ports in the calibration, otherwise ports can be specified where the DUT is connected.
        """
        self.CalculateErrorTerms()
        if pl is None: pl = [p for p in range(self.ports)]
        ports=len(pl)
        return [SParameters(self.f,[
                vstack((hstack((matrix(self[n].Fixture(p,pl)[0][0]),
                                matrix(self[n].Fixture(p,pl)[0][1]))),
                        hstack((matrix(self[n].Fixture(p,pl)[1][0]),
                                matrix(self[n].Fixture(p,pl)[1][1]))))).tolist()
                    for n in range(len(self))]) for p in range(ports)]
    def WriteFixturesToFiles(self,filename,pl=None):
        """Writes the error terms to a files in the form of fixtures
        @param filename prefix of the files to write the error terms to.
        @param pl (optional) list of zero based port numbers of the DUT

        For a P port calibration, this writes P s-parameter files where each
        file is a 2P port fixture file.
        @remark If the portList is None, then it assumed to be a list [0,1,2,P-1] where P is the
        number of ports in the calibration, otherwise ports can be specified where the DUT is connected.

        """
        self.CalculateErrorTerms()
        if pl is None: pl = [p for p in range(self.ports)]
        ports=len(pl)
        Fixture=self.Fixtures(pl)
        for p in range(ports):
            Fixture[p].WriteToFile(filename+str(p+1))
        return self
    def WriteToFile(self,filename,pl=None):
        """Writes the error terms to a file in LeCroy format
        @param filename name of file to write the error terms to
        @param pl (optional) list of zero based port numbers of the DUT.

        The LeCroy format is for each row, for each column, for each error-term,
        for each frequency point, the error term is written on a line as the real and imaginary part.
        the first line of the file contains three numbers, the number of ports, the number of frequency
        points (-1) and the end frequency.
        @remark If the portList is None, then it assumed to be a list [0,1,2,P-1] where P is the
        number of ports in the calibration, otherwise ports can be specified where the DUT is connected.
        """
        self.CalculateErrorTerms()
        if pl is None: pl = [p for p in range(self.ports)]
        ports=len(pl)
        lines=[]
        numPoints=len(self)
        endFrequency=self.f[-1]
        lines.append(str(ports)+' '+str(numPoints-1)+' '+str(endFrequency)+'\n')
        for r in range(ports):
            for c in range(ports):
                for t in range(3):
                    for n in range(numPoints):
                        et=self[n].ET[pl[r]][pl[c]][t]
                        lines.append('%15.10e ' % et.real + '%15.10e\n' % et.imag)
        with open(filename,'w') as f:
            f.writelines(lines)
        return self
    def ReadFromFile(self,filename):
        """Reads the error terms to a file in LeCroy format
        @param filename name of file to read the error terms from
        @return self

        The LeCroy format is for each row, for each column, for each error-term,
        for each frequency point, the error term is written on a line as the real and imaginary part.
        the first line of the file contains three numbers, the number of ports, the number of frequency
        points (-1) and the end frequency.
        """
        with open(filename,'rU' if sys.version_info.major < 3 else 'r') as f:
            lines=f.readlines()
        tokens=lines[0].split(' ')
        self.ports=int(tokens[0])
        numPoints=int(tokens[1])
        endFrequency=float(tokens[2])
        self.f=EvenlySpacedFrequencyList(endFrequency,numPoints)
        self.calibrationMatrix=[[[] for _ in range(self.ports)]
                                for _ in range(self.ports)]
        self.ET=[ErrorTerms().Initialize(self.ports) for n in range(numPoints+1)]
        lineIndex=1
        for r in range(self.ports):
            for c in range(self.ports):
                for t in range(3):
                    for n in range(numPoints+1):
                        lineStrings=lines[lineIndex].split(' ')
                        lineIndex=lineIndex+1
                        self[n].ET[r][c][t]=float(lineStrings[0])+1j*float(lineStrings[1])
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
                (calibrationMeasurement.type=='xtalk') or\
                (calibrationMeasurement.type=='reciprocal'):
                portDriven=calibrationMeasurement.portDriven
                otherPort=calibrationMeasurement.otherPort
                self.calibrationMatrix[otherPort][portDriven].\
                    append(calibrationMeasurement)
        return self
    def _CalculateReflectErrorTerms(self,measurements):
        """calculates the reflect error terms ED, ER, ES for all ports and frequencies.
        @param measurements list of list of calibration measurements where each column corresponds to
        a driven port and each row corresponds to a measured port.
        """
        for port in range(self.ports):
            measurementList=measurements[port][port]
            for n in range(len(self)):
                hatGamma=[meas.gamma[n] for meas in measurementList]
                Gamma=[meas.Gamma[n][0][0] for meas in measurementList]
                self[n].ReflectCalibration(hatGamma,Gamma,port)
    def _CalculateXtalkErrorTerms(self,measurements):
        """calculates the crosstalk error terms EX for all port combinations and frequencies.
        @param measurements list of list of calibration measurements where each column corresponds to
        a driven port and each row corresponds to a measured port.
        """
        for other in range(self.ports):
            for driven in range(self.ports):
                if (other != driven):
                    measurementList=measurements[other][driven]
                    xtalkMeasurementList=[]
                    for meas in measurementList:
                        if meas.type=='xtalk': xtalkMeasurementList.append(meas)
                    if len(xtalkMeasurementList)!=0:
                        for n in range(len(self.f)):
                            self[n].ExCalibration(
                                xtalkMeasurementList[0].b2a1[n],other,driven)
    def _CalculateUnknownThruErrorTerms(self,measurements):
        """calculates the unknown thru standards for each unknown thru measurement.
        @param measurements list of list of calibration measurements where each column corresponds to
        a driven port and each row corresponds to a measured port.
        @remark measurements is affected by this function and the returned measurements should be used
        subsequently.  Unknown thru measurements create thru measurements using the recovered thru standards.
        """
        for other in range(self.ports):
            for driven in range(self.ports):
                if (other != driven):
                    for meas in measurements[other][driven]:
                        if meas.type=='reciprocal':
                            Sestsp= [s for s in meas.S] if not (meas.S is None)\
                                else [Thru() for _ in range(len(self.f))]
                            for n in range(len(self.f)):
                                Sestsp[n]=self[n].UnknownThruCalibration(
                                    meas.Smeasured[n],
                                    Sestsp[n] if not meas.S is None
                                    else Sestsp[max(n-1,0)],driven,other)
                            Sest=SParameters(self.f,Sestsp)
                            Sest=Sest.LimitImpulseResponseLength(meas.limit)
                            measurements[other][driven].append(
                                ThruCalibrationMeasurement(
                                meas.Smeasured.FrequencyResponse(1,1),
                                meas.Smeasured.FrequencyResponse(2,1),
                                Sest,other,driven))
                            measurements[driven][other].append(
                                ThruCalibrationMeasurement(
                                meas.Smeasured.FrequencyResponse(2,2),
                                meas.Smeasured.FrequencyResponse(1,2),
                                Sest.PortReorder([1,0]),driven,other))
    def _CalculateThruErrorTerms(self,measurements):
        """calculates the thru error terms EL and ET for each port combination and frequency.
        @param measurements list of list of calibration measurements where each column corresponds to
        a driven port and each row corresponds to a measured port.
        """
        for other in range(self.ports):
            for driven in range(self.ports):
                if (other != driven):
                    measurementList=measurements[other][driven]
                    thruMeasurementList=[]
                    for meas in measurementList:
                        if meas.type=='thru': thruMeasurementList.append(meas)
                    if len(thruMeasurementList)!=0:
                        for n in range(len(self.f)):
                            b1a1=[meas.b1a1[n] for meas in thruMeasurementList]
                            b2a1=[meas.b2a1[n] for meas in thruMeasurementList]
                            S=[meas.S[n] for meas in thruMeasurementList]
                            self[n].ThruCalibration(b1a1,b2a1,S,other,driven)
    def _CalculateTransferThruErrorTerms(self):
        """calculates the transfer thru error terms EL and ET for each port combination and frequency not
        already covered by an actual thru calibration.
        @param measurements list of list of calibration measurements where each column corresponds to
        a driven port and each row corresponds to a measured port.
        """
        if Calibration.FillInTransferThru:
            for n in range(len(self.f)): self[n].TransferThruCalibration()
    def CalculateErrorTerms(self,force=False):
        """Calculates the error terms

        The error terms are calculated in a specific order so that dependencies can be satisfied.

        The reflect error terms are computed first, then the crosstalk error terms.  The unknown thru
        error terms are calculated which need the reflect and crosstalk error terms.  The unknown thru
        recovers the thru which is passed to thru error terms calculations (the reason for this is to
        allow for multiple thru standards computations).  Finally, the transfer thru error terms are
        calculated which depend on the thru error terms.
        @param force (optional) boolean whether to force it to calculate the error terms.
        @remark If error terms have not been calculated or force, then the error terms are calculated
        from instances of CalibrationMeasurement provided during the calibration."""
        if (not self.ET is None) and (not force): return self
        self.ET=[ErrorTerms().Initialize(self.ports) for _ in range(len(self))]
        measurements=copy.deepcopy(self.calibrationMatrix)
        self._CalculateReflectErrorTerms(measurements)
        self._CalculateXtalkErrorTerms(measurements)
        self._CalculateUnknownThruErrorTerms(measurements)
        self._CalculateThruErrorTerms(measurements)
        self._CalculateTransferThruErrorTerms()
        return self
    def DutCalculationAlternate(self,sRaw,portList=None,reciprocal=False):
        """Alternate Dut Calculation
        @deprecated This provides a DUT calculation according to the Wittwer method,
        but a better,simpler method has been found.

        converts the raw measured s-parameters of the DUT into calibrated s-parameter
        measurements.\n
        If the portList is None, then it assumed to be a list [0,1,2,P-1] where P is the
        number of ports in sRaw, otherwise ports can be specified where the DUT is connected.
        @param sRaw instance of class SParameters of the raw measurement of the DUT.
        @param portList (optional) list of zero based port numbers of the DUT
        @param reciprocal (optional, defaults to False) whether to enforce reciprocity
        @return instance of class SParameters of the calibrated DUT measurement.
        @remark if reciprocity is True, the reciprocity is enforced in the calculation
        """
        self.CalculateErrorTerms()
        return SParameters(self.f,[self[n].DutCalculationAlternate(sRaw[n],portList,reciprocal)
                                   for n in range(len(self))])
    def DutCalculation(self,sRaw,portList=None,reciprocal=False):
        """calculates the Dut.\n
        converts the raw measured s-parameters of the DUT into calibrated s-parameter
        measurements.\n
        If the portList is None, then it assumed to be a list [0,1,2,P-1] where P is the
        number of ports in sRaw, otherwise ports can be specified where the DUT is connected.
        @param sRaw instance of class SParameters of the raw measurement of the DUT.
        @param portList (optional) list of zero based port numbers of the DUT
        @param reciprocal (optional, defaults to False) whether to enforce reciprocity
        @return instance of class SParameters of the calibrated DUT measurement.
        @remark if reciprocity is True, the reciprocity is enforced in the calculation
        """
        self.CalculateErrorTerms()
        return SParameters(self.f,[self[n].DutCalculation(sRaw[n],portList,reciprocal)
                                   for n in range(len(self))])
    def DutUnCalculationAlternate(self,S,portList=None):
        """Un-calcualates the DUT.\n
        This calculates the expected raw measured DUT based on the DUT actually calculated.\n
        @see DutCalculation
        @param S instance of class SParameters of measured DUT from these error-terms.
        @param portList (optional) list of zero based port numbers used for the DUT calcualtion
        @return instance of class SParameters of the raw measured s-parameters that calculated this DUT
        @remark If the portList is None, then it assumed to be a list [0,1,2,P-1] where P is the
        number of ports in sRaw, otherwise ports can be specified where the DUT is connected.
        @deprecated This method utilizes fixtures and embeds them.  Originally, I could not figure out
        how to do this with just the error-terms.  This was figured out finally and is more efficient, but
        this method is retained for comparison of results.
        @see DutUnCalculation
        """
        self.CalculateErrorTerms()
        if portList is None: portList=[p for p in range(self.ports)]
        ports=len(portList)

        sspn=SystemSParametersNumeric()
        sspn.AddDevice('F',2*ports)
        sspn.AddDevice('D',ports)
        for p in range(ports):
            sspn.AddPort('F',p+1,p+1)
            sspn.ConnectDevicePort('F',ports+p+1,'D',p+1)

        rd=[None for n in range(len(self.f))]
        fixtureList=self.Fixtures(portList)
        for n in range(len(self.f)):
            rm=[[None for c in range(ports)] for r in range(ports)]
            sspn.AssignSParameters('D',S[n])
            for p in range(ports):
                sspn.AssignSParameters('F',fixtureList[p][n])
                spp=sspn.SParameters()
                for r in range(ports):
                    rm[r][p]=spp[r][p]
            rd[n]=rm
        return SParameters(self.f,rd)
    def DutUnCalculation(self,S,portList=None):
        """Un-calcualates the DUT.\n
        This calculates the expected raw measured DUT based on the DUT actually calculated.\n
        @see DutCalculation
        @param S instance of class SParameters of measured DUT from these error-terms.
        @param portList (optional) list of zero based port numbers used for the DUT calcualtion
        @return instance of class SParameters of the raw measured s-parameters that calculated this DUT
        @remark If the portList is None, then it assumed to be a list [0,1,2,P-1] where P is the
        number of ports in sRaw, otherwise ports can be specified where the DUT is connected.
        """
        self.CalculateErrorTerms()
        return SParameters(self.f,[self[n].DutUnCalculation(S[n],portList)
                                   for n in range(len(self))])