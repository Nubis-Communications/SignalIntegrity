"""
 base class for calibration netlist handling
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

from SignalIntegrity.Lib.Measurement.Calibration.Calibration import Calibration
from SignalIntegrity.Lib.Measurement.Calibration.CalibrationMeasurements import *
from SignalIntegrity.Lib.Parsers.SystemDescriptionParser import SystemDescriptionParser
from SignalIntegrity.Lib.SParameters.SParameterFile import SParameterFile
from SignalIntegrity.Lib.Exception import SignalIntegrityExceptionCalibration
import copy

class CalibrationParser(SystemDescriptionParser):
    """base class for netlist based error terms solutions"""
    def __init__(self, f=None, args=None):
        """Constructor  
        frequencies may be provided at construction time (or not for symbolic solutions).
        @param f (optional) list of frequencies
        @param args (optional) string arguments for the circuit.
        @remark Arguments are provided on a line as pairs of names and values separated by a space.
        """
        SystemDescriptionParser.__init__(self, f, args)
        self.ports=0
        self.calibrationMeasurementList=None
    def _ProcessCalibrationLine(self,line):
        """processes a line of a netlist, handing calibration specific commands.  
        Lines that can be processed at this level are processed and lines that
        are unknown are place in a list of unknown lines for upstream processing.  This
        enables derived classes to benefit from what this class knows how to process and
        to simply add specific functionality.  As a simple example, a derived simulator class
        needs to add output probes, and this simple system description class knows nothing of
        this.  
        netlist lines that are handled at this level are:
        - 'calibration' - handling of calibration measurements
        @todo document the exact syntax of the netlist lines processed here.
        """
        lineList=self.ReplaceArgs(line.split())
        if len(lineList) == 0: return
        if lineList[0] == 'calibration':
            if self.calibrationMeasurementList == None: self.calibrationMeasurementList = []
            if lineList[1] in ['reflect','thru','xtalk']:
                if self.calibrationMeasurementList is None: self.calibrationMeasurementList=[]
                measDict={}
                measDict['type']=lineList[1]
                for i in range(2,len(lineList),2):
                    tokenName,tokenValue = lineList[i],lineList[i+1]
                    if tokenName == 'file':
                        measDict['raw']=SParameterFile(tokenValue).Resample(self.m_f)
                    elif tokenName == 'std':
                        if tokenValue == 'None':
                            self.m_spc[tokenValue] = None
                        elif not tokenValue in self.m_spc:
                            self.m_spc[tokenValue] = SParameterFile(tokenValue).Resample(self.m_f)
                        measDict['std']=self.m_spc[tokenValue]
                    elif tokenName == 'pn':
                        measDict['driven']=port=int(tokenValue)
                        self.ports=max(port,self.ports)
                    elif tokenName == 'opn':
                        measDict['other']=port=int(tokenValue)
                        self.ports=max(port,self.ports)
                    elif tokenName == 'ct':
                        measDict['thrutype']=tokenValue
                if measDict['type']=='reflect':
                    self.calibrationMeasurementList.append(ReflectCalibrationMeasurement(measDict['raw'].FrequencyResponse(1,1),
                        measDict['std'],
                        measDict['driven']-1))
                elif measDict['type']=='thru':
                    if measDict['thrutype']=='SOLT':
                        self.calibrationMeasurementList.append(ThruCalibrationMeasurement(measDict['raw'].FrequencyResponse(1,1),
                            measDict['raw'].FrequencyResponse(2,1),measDict['std'],measDict['driven']-1,measDict['other']-1))
                        self.calibrationMeasurementList.append(ThruCalibrationMeasurement(measDict['raw'].FrequencyResponse(2,2),
                            measDict['raw'].FrequencyResponse(1,2),measDict['std'],measDict['other']-1,measDict['driven']-1))
                    elif measDict['thrutype']=='SOLR':
                        self.calibrationMeasurementList.append(UnknownThruCalibrationMeasurement(measDict['raw'],
                            measDict['std'],measDict['driven']-1,measDict['other']-1))
                elif measDict['type']=='xtalk':
                    self.calibrationMeasurementList.append(XtalkCalibrationMeasurement(measDict['raw'].FrequencyResponse(2,1),
                            measDict['driven']-1,measDict['other']-1))
                    self.calibrationMeasurementList.append(XtalkCalibrationMeasurement(measDict['raw'].FrequencyResponse(1,2),
                            measDict['other']-1,measDict['driven']-1))
        else: self.m_ul.append(line)
    def _ProcessLines(self):
        """processes all of the lines in a netlist
        @see _ProcessLine() for explanation of parameters and functionality.
        """
        SystemDescriptionParser._ProcessLines(self)
        self.m_spc={key:value.Resample(self.m_f) for (key,value) in self.m_spc}
        lines=copy.deepcopy(self.m_ul); self.m_ul=[]
        for i in range(len(lines)):
            line=lines[i]
            self._ProcessCalibrationLine(line)
            # pragma: silent exclude
            if self.HasACallBack():
                progress=(float(i)+1)/len(lines)*100.0
                if not self.CallBack(progress):
                    raise SignalIntegrityExceptionCalibration('calculation aborted')
            # pragma: include
        self.calibration = Calibration(self.ports,self.m_f)
        self.calibration.AddMeasurements(self.calibrationMeasurementList)
        return self