"""
SineWaveform.py
"""

# Copyright (c) 2021 Nubis Communications, Inc.
# Copyright (c) 2018-2020 Teledyne LeCroy, Inc.
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
import numpy as np

from SignalIntegrity.Lib.TimeDomain.Waveform.Waveform import Waveform
from SignalIntegrity.Lib.TimeDomain.Waveform.PulseWaveform import PulseWaveform

class SineWaveform(Waveform):
    """sinewave waveform"""
    def __init__(self,td,Amplitude=1.,Frequency=1e6,Phase=0.,
                 StartTime=-100.,StopTime=100.):
        """Constructor  
        constructs a sinewave waveform.
        @param td instance of class TimeDescriptor containing time axis of waveform.
        @param Amplitude (optional) float amplitude of sine wave (defaults to unity).
        @param Frequency (optional) float frequency of sine wave (defaults to 1 MHz).
        @param Phase (optional) float phase of sine wave in degrees (defaults to zero).
        @param StartTime (optional) float start time of sine wave (defaults to -100 s).
        @param StopTime (optional) float stop time of the sine wave (defaults to 100 s).
        """
        times=np.asarray(td.Times())
        x=Amplitude*np.sin(2.*math.pi*Frequency*times+Phase/180.*math.pi)
        sw=Waveform(td,x)*PulseWaveform(td,Amplitude=1.,StartTime=StartTime,
            PulseWidth=max(StartTime,StopTime)-min(StartTime,StopTime),Risetime=0.)
        Waveform.__init__(self,sw.td,sw.Values())