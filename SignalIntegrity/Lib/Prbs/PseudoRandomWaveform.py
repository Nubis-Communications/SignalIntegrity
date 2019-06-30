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
from SignalIntegrity.Lib.Prbs.PseudoRandomPolynomial import PseudoRandomPolynomial
from SignalIntegrity.Lib.Exception import SignalIntegrityExceptionWaveform,SignalIntegrityException
from SignalIntegrity.Lib.Prbs.SerialDataWaveform import SerialDataWaveform

class PseudoRandomWaveform(SerialDataWaveform):
    """a PRBS waveform with a given PRBS polynomial"""
    def __init__(self,polynomial,bitrate,amplitude=1.0,risetime=0.,delay=0.,tdOrFs=None):
        """constructor
        @param polynomial integer polynomial number
        @param bitrate, amplitude, risetime, delay, tdOrFs all pertain to the derived SerialDataWaveform class
        @see SerialDataWaveform
        @return self, a waveform.
        @throw SignalIntegrityWaveform exception is raised if the polynomial number cannot be found
        @see PseudoRandomPolynomial
        """
        try:
            SerialDataWaveform.__init__(self,PseudoRandomPolynomial(polynomial).Pattern(),bitrate,amplitude,risetime,delay,tdOrFs)
        except SignalIntegrityException as e:
            raise SignalIntegrityExceptionWaveform(e.message)
