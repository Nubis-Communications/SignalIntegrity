"""
StepWaveform.py
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

from SignalIntegrity.Lib.TimeDomain.Waveform.Waveform import Waveform
import math

class StepWaveform(Waveform):
    """step waveform"""
    rtvsT=0.5903445
    def __init__(self,td,Amplitude=1.,StartTime=0.,risetime=0.):
        """Constructor

        constructs a step waveform.

        @param td instance of class TimeDescriptor containing time axis of waveform.
        @param Amplitude (optional) float amplitude of step (defaults to unity).
        @param StartTime (optional) float starting time of the pulse (defaults to zero).
        @param risetime (optional) float risetime in seconds (defaults to 0.)

        @note The amplitude can be positive or negative, with negative providing a negative
        pulse.
        @note The step starts at the first sample point after the start time specified.
        @note actual risetime used is the sample period if less than that is specified
        @note the risetime is applied such that the step reaches half amplitude at the start
        time specified.  Please note the expected non-causality.
        """
        x=[0 if t < StartTime else Amplitude for t in td.Times()]
        T=risetime/self.rtvsT
        rcStart=max(0,td.IndexOfTime(StartTime-T/2.))
        if td.TimeOfPoint(rcStart)<StartTime-T/2: rcStart=min(rcStart+1,len(td)-1)
        rcEnd=min(len(td)-1,td.IndexOfTime(StartTime+T/2.))
        if td.TimeOfPoint(rcEnd)>StartTime+T/2: rcEnd=max(rcEnd-1,0)
        for i in range(rcStart,rcEnd+1):
            try:
                x[i]=Amplitude*\
                    (math.sin((td.TimeOfPoint(i)-StartTime)/T*math.pi)+1.)/2.
            except ZeroDivisionError:
                pass
        Waveform.__init__(self,td,x)