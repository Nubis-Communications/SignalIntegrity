"""
 SSPRQ waveform
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
import pathlib

from SignalIntegrity.Lib.TimeDomain.Waveform import Waveform
from SignalIntegrity.Lib.Prbs.PseudoRandomPolynomial import PseudoRandomPolynomial
from SignalIntegrity.Lib.Prbs.SerialDataWaveform import SerialDataWaveform

class SSPRQWaveform(Waveform):
    """a SSPRQ PAM4 waveform with a given rise time and amplitude"""
    def __init__(self, baudrate, amplitude=1.0,risetime=0.,delay=0.,td=None):
        """constructor
        @param baudrate, amplitude, risetime, delay, td all pertain to the derived SerialDataWaveform class
        @see SerialDataWaveform
        @return self, a waveform.
        @note the pseudo-random bits are grouped for each symbol.
        """
        symbols=int(math.ceil(td.Duration()*baudrate))
        bitsPerSymbol = 2 #PAM4 is assumed for SSPRQ (not defined otherwise)
        levels= bitsPerSymbol**2
        pattern_load =  np.loadtxt(pathlib.Path(__file__).parent / 'SSPRQ.txt') #load in SSPRQ
        pattern = [int((x + 1) * 3/2) for x in pattern_load] #Scale pattern from -1 to 1 to 0 to 3 for easy processing
        wf=sum([SerialDataWaveform([int(pattern[i %(len(pattern))] / (bitsPerSymbol ** (bitsPerSymbol - k - 1))) %  2 for i in range(symbols)],
                baudrate,pow(2.,(bitsPerSymbol-k-1.))/(levels-1)*amplitude,risetime,delay,td) for k in range(bitsPerSymbol)])
        Waveform.__init__(self,wf)


if __name__ == "__main__":
    import SignalIntegrity.Lib as si
    td = si.td.wf.TimeDescriptor(HorOffset=0, NumPts=850000, SampleRate = 2)
    ssprq = SSPRQWaveform(baudrate=1, amplitude=1, risetime = 0, delay = 0, td=td)
    print('done')