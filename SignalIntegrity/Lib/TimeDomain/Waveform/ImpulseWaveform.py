"""
ImpulseWaveform.py
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

from SignalIntegrity.Lib.TimeDomain.Waveform.Waveform import Waveform

class ImpulseWaveform(Waveform):
    """pulse waveform"""
    def __init__(self,td,Amplitude=1.,StartTime=0.):
        """Constructor  
        constructs a waveform with a single pulse.
        @param td instance of class TimeDescriptor containing time axis of waveform.
        @param Amplitude (optional) float amplitude of pulse (defaults to unity).
        @param StartTime (optional) float starting time of the pulse (defaults to zero).
        @note The impulse will appear on the sample that is the closest to the start time specified.
        """
        index_of_impulse=round(td.IndexOfTime(StartTime,Integer=False))
        Waveform.__init__(self,td,[Amplitude if k == index_of_impulse else 0 for k in range(td.K)])