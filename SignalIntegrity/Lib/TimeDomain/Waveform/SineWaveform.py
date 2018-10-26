"""
SineWaveform.py
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

class SineWaveform(Waveform):
    """sinewave waveform"""
    def __init__(self,td,Amplitude=1.,Frequency=1e6,Phase=0.):
        """Constructor

        constructs a sinewave waveform.

        @param td instance of class TimeDescriptor containing time axis of waveform.
        @param Amplitude (optional) float amplitude of sine wave (defaults to unity).
        @param Frequency (optional) float frequency of sine wave (defaults to 1 MHz).
        @param Phase (optional) float phase of sine wave in degrees (defaults to zero).
        """
        x=[Amplitude*math.sin(2.*math.pi*Frequency*t+Phase/180.*math.pi)
                for t in td.Times()]
        Waveform.__init__(self,td,x)