"""
SParameterCalculator.py
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
from SignalIntegrity.Lib.SParameters.SParameters import SParameters
from SignalIntegrity.Lib.FrequencyDomain.FrequencyList import EvenlySpacedFrequencyList

class SParameterCalculator(object):
    def __init__(self):
        import win32com.client as win32
        self.comObject = win32.Dispatch(r'OysterSparameterCalcSvr.OysterCalc')
    def PutWaveform(self,wf):
        import win32com.client as win32
        import array
        self.comObject.PutMeasurement(
            win32.VARIANT(win32.pythoncom.VT_R8 | win32.pythoncom.VT_BYREF | win32.pythoncom.VT_ARRAY,
            array.array('d',wf.Times())),
            win32.VARIANT(win32.pythoncom.VT_R8 | win32.pythoncom.VT_BYREF | win32.pythoncom.VT_ARRAY,
            array.array('d',wf.Values())))
    def PutSettings(self,sdict):
        for key in sdict:
            attr=key
            value=sdict[key]
            from win32com.client.dynamic import _GetDescInvokeType
            import pythoncom
            if self.comObject.__LazyMap__(attr):
                if attr in self.comObject._olerepr_.propMapPut:
                    entry = self.comObject._olerepr_.propMapPut[attr]
                    invoke_type = _GetDescInvokeType(entry, pythoncom.INVOKE_PROPERTYPUT)
                    self.comObject._oleobj_.Invoke(entry.dispid, 0, invoke_type, 0, value)
    def SParameterResult(self,wfDict=None):
        if not wfDict is None:
            numSwitchSettings = self.comObject.NumSwitchSettingsRequired
            for s in range(numSwitchSettings):
                self.comObject.SwitchSettingNumber = s
                relaySettings=self.comObject.RelaySettings
                #measurementName = self.comObject.MeasurementName
                pulserString=self.comObject.PulsersToTurnOn
                pulserList=[int(p) for p in pulserString.split(',')]
                samplerString=self.comObject.SamplersToMeasure
                samplersList=[[int(sa) for sa in p.split(',')] for p in samplerString.split(';')]
                for d in range(len(pulserList)):
                    drivenPort=pulserList[d]
                    self.comObject.DrivenPort=drivenPort
                    for m in range(len(samplersList[d])):
                        if self._IsDutMeasurement(relaySettings):
                            #print s,d,m
                            measuredPort=samplersList[d][m]
                            self.comObject.MeasuredPort=measuredPort
                            print(relaySettings+' driven: '+str(drivenPort)+' meas: '+str(measuredPort)+' name: '+wfDict[relaySettings][drivenPort][measuredPort]['name'])
                            self.PutWaveform(wfDict[relaySettings][drivenPort][measuredPort]['wf'])
        self.comObject.Calculate()
        numPorts=self.comObject.NumPortsInMeasurement
        numPoints=self.comObject.NumPoints
        Fe=self.comObject.EndFrequency
        sp=SParameters(EvenlySpacedFrequencyList(Fe,numPoints),[[[0.0 for _ in range(numPorts)] for _ in range(numPorts)] for _ in range(numPoints+1)])
        for r in range(numPorts):
            for c in range(numPorts):
                resrvar=self.comObject.NewResults('s['+str(r+1)+']['+str(c+1)+'],Real')
                rescvar=self.comObject.NewResults('s['+str(r+1)+']['+str(c+1)+'],Imag')
                for n in range(numPoints+1):
                    sp[n][r][c]=resrvar[n][1]+1j*rescvar[n][1]
        return sp
    def _IsCalibrationMeasurement(self,relaySetting):
            return relaySetting in ['S,S,S,S,X,X,X,X,X,X',
                                        'O,O,O,O,X,X,X,X,X,X',
                                        'L,L,L,L,X,X,X,X,X,X',
                                        'RS2,RS1,RS4,RS3,X,X,X,X,X,X',
                                        'RS4,RS3,RS2,RS1,X,X,X,X,X,X']
    def _IsDutMeasurement(self,relaySetting):
            return not self._IsCalibrationMeasurement(relaySetting)
    def Calibrate(self,wfDict,calculate=False):
        numSwitchSettings = self.comObject.NumSwitchSettingsRequired
        for s in range(numSwitchSettings):
            self.comObject.SwitchSettingNumber = s
            relaySettings=self.comObject.RelaySettings
            #measurementName = self.comObject.MeasurementName
            pulserString=self.comObject.PulsersToTurnOn
            pulserList=[int(p) for p in pulserString.split(',')]
            samplerString=self.comObject.SamplersToMeasure
            samplersList=[[int(sa) for sa in p.split(',')] for p in samplerString.split(';')]
            for d in range(len(pulserList)):
                drivenPort=pulserList[d]
                self.comObject.DrivenPort=drivenPort
                for m in range(len(samplersList[d])):
                    if self._IsCalibrationMeasurement(relaySettings):
                        #print s,d,m
                        measuredPort=samplersList[d][m]
                        self.comObject.MeasuredPort=measuredPort
                        print(relaySettings+' driven: '+str(drivenPort)+' meas: '+str(measuredPort)+' name: '+wfDict[relaySettings][drivenPort][measuredPort]['name'])
                        self.PutWaveform(wfDict[relaySettings][drivenPort][measuredPort]['wf'])
        if calculate: self.comObject.Calculate()

