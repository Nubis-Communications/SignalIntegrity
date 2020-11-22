"""
 multi-level waveform
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

from SignalIntegrity.Lib.TimeDomain.Waveform import Waveform
from SignalIntegrity.Lib.Prbs.PseudoRandomPolynomial import PseudoRandomPolynomial
from SignalIntegrity.Lib.Prbs.SerialDataWaveform import SerialDataWaveform

class MultiLevelWaveform(Waveform):
    """a PRBS multi-level waveform with a given PRBS polynomial"""
    def __init__(self,polynomial,baudrate,bitsPerSymbol=1,amplitude=1.0,risetime=0.,delay=0.,td=None):
        """constructor
        @param polynomial integer polynomial number
        @param baudrate, amplitude, risetime, delay, td all pertain to the derived SerialDataWaveform class
        @see SerialDataWaveform
        @param bitsPerSymbol integer (defaults to 1) are the number of bits per symbol and determines the number
        of levels in the waveform.  bitsPerSymbol = 1, means NRZ, 2 means PAM-4, 3 means PAM-8 etc.
        @return self, a waveform.
        @throw SignalIntegrityWaveform exception is raised if the polynomial number cannot be found
        @see PseudoRandomPolynomial
        @note the pseudo-random bits are grouped for each symbol.
        """
        symbols=int(math.ceil(td.Duration()*baudrate)); levels=pow(2,bitsPerSymbol)
        pattern=PseudoRandomPolynomial(polynomial).Pattern(symbols*bitsPerSymbol)
        wf=sum([SerialDataWaveform([pattern[(i*bitsPerSymbol+k)%(len(pattern))] for i in range(symbols)],
                baudrate,pow(2.,(bitsPerSymbol-k-1.))/(levels-1)*amplitude,risetime,delay,td) for k in range(bitsPerSymbol)])
        Waveform.__init__(self,wf)
