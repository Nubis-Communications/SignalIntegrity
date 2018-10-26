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

class StepWaveform(Waveform):
    """step waveform"""
    def __init__(self,td,Amplitude=1.,StartTime=0.):
        """Constructor

        constructs a step waveform.

        @param td instance of class TimeDescriptor containing time axis of waveform.
        @param Amplitude (optional) float amplitude of step (defaults to unity).
        @param StartTime (optional) float starting time of the pulse (defaults to zero).

        @note The amplitude can be positive or negative, with negative providing a negative
        pulse.
        @note The step starts at the first sample point after the start time specified.
        """
        x=[0 if t < StartTime else Amplitude for t in td.Times()]
        Waveform.__init__(self,td,x)