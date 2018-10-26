"""
NoiseWaveform.py
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
import numpy

class NoiseWaveform(Waveform):
    """noise waveform"""
    def __init__(self,td,sigma,mean=0.0):
        """Constructor

        constructs a waveform with mean and normally distributed noise.

        @param td instance of class TimeDescriptor containing time axis of waveform.
        @param sigma float non-zero value of the rms value of the noise
        @param mean (optional) float containing the mean value of the waveform
        """
        Waveform.__init__(self,td,numpy.random.normal(mean,sigma,int(td.K)).tolist())