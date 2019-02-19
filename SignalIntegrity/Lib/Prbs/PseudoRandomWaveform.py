"""
 pseudo-random waveform
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
import math
from SignalIntegrity.Lib.TimeDomain.Waveform.Waveform import Waveform
from SignalIntegrity.Lib.TimeDomain.Waveform.TimeDescriptor import TimeDescriptor
from SignalIntegrity.Lib.Prbs.PseudoRandomBitPattern import PseudoRandomBitPattern

class SerialDataWaveform(Waveform):
    rtvsT=0.5903445
    def __init__(self,pattern,bitRate,amplitude=1.0,risetime=0.,tdOrFs=None):
        if tdOrFs is None:
            sampleRate=10.*bitRate
            td=self.TimeDescriptor(bitRate, sampleRate, len(pattern))
        elif isinstance(tdOrFs,float):
            sampleRate=tdOrFs
            td=self.TimeDescriptor(bitRate, sampleRate, len(pattern))
        else:
            td=tdOrFs
        patternTimeLength=len(pattern)/bitRate
        unitInterval=1./bitRate
        wf=(Waveform(td,[sum([(self.UnitPulse((td[k]-(i-1)*unitInterval)%patternTimeLength,risetime,unitInterval)-0.5)*pattern[i]
            for i in range(len(pattern))]) for k in range(len(td))])+(float(sum(pattern))/2-0.5))*(2.*amplitude)
        Waveform.__init__(self,wf)
    @staticmethod
    def TimeDescriptor(bitRate,sampleRate,patternLength):
        timeLength=patternLength/bitRate
        numPoints=int(math.floor(timeLength*sampleRate+0.5))
        return TimeDescriptor(0.,numPoints,sampleRate)
    @staticmethod
    def RaisedCosine(t,T):
        """raised cosine
        @return the value of a raised cosine edge that is zero for t<0 and 1 for t>T.
        @remark the risetime of this edge is 59% of the value of T
        """
        if t < 0: return 0.
        elif t > T: return 1.
        else: return 1./2-1./2*math.cos(math.pi*t/T)
    def UnitPulse(self,t,risetime,unitInterval):
        T=risetime/self.rtvsT
        return self.RaisedCosine(t-T/2,T)-self.RaisedCosine(t-T/2-unitInterval,T)

class PseudoRandomWaveform(SerialDataWaveform):
    def __init__(self,polynomial,bitrate,amplitude=1.0,risetime=0.,tdOrFs=None):
        SerialDataWaveform.__init__(self,PseudoRandomBitPattern(polynomial),bitrate,amplitude,risetime,tdOrFs)            
