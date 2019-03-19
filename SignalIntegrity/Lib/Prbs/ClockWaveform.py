"""
 clock waveform
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
from SignalIntegrity.Lib.Exception import SignalIntegrityExceptionWaveform,SignalIntegrityException
from SignalIntegrity.Lib.Prbs.SerialDataWaveform import SerialDataWaveform

class ClockWaveform(SerialDataWaveform):
    """a clock waveform"""
    def __init__(self,clockfrequency,amplitude=1.0,risetime=0.,delay=0.,tdOrFs=None):
        """constructor
        @param clockfrequency float rate of clock in Hz
        @param amplitude, risetime, delay, tdOrFs all pertain to the derived SerialDataWaveform class
        @see SerialDataWaveform
        @return self, a waveform.
        @note this uses the serial data waveform class with bitrate specified as half the clock frequency
        and a bitrate of twice the clockfreqeuncy.
        """
        SerialDataWaveform.__init__(self,[1,0],clockfrequency*2,amplitude,risetime,delay,tdOrFs)


