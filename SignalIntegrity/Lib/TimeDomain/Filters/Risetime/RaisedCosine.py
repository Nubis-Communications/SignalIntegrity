"""
RaisedCosine.py
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

from SignalIntegrity.Lib.TimeDomain.Filters.FirFilter import FirFilter
from SignalIntegrity.Lib.TimeDomain.Waveform import TimeDescriptor
from SignalIntegrity.Lib.TimeDomain.Waveform.ImpulseResponse import ImpulseResponse
from SignalIntegrity.Lib.TimeDomain.Waveform.Waveform import Waveform

class RaisedCosine(FirFilter):
    """
    Raised cosine FIR filter that, when convolved with step, provides
    the risetime specified at the given sample rate.
    """
    a2080=3.054676 # hardcoded relationship that produces 20-80 risetime
    a1090=2.07388 # hardcoded relationship that produces 10-90 risetime
    def __init__(self,rt,Fs,is1090=True):
        """constructor
        @param rt float risetime desired.
        @param Fs float sample rate
        @param is1090 boolean (optional, defaults to True) whether 10-90 risetime
        is specified.  Otherwise 20-80 risetime is used.
        """
        import numpy as np
        a=self.a1090 if is1090 else self.a2080
        K=int(np.ceil(rt*a*Fs/2))*2+1 # guaranteed to be odd
        h=[0 for _ in range(K)]
        H=-(K-1)//2/Fs # time of first point
        for k in range(K):
            t=H+k/Fs
            h[k]=0.5-0.5*np.cos((t+rt*a/2.)/(rt*a)*2.*np.pi) if -rt*a/2. <= t <= rt*a/2. else 0
        td=TimeDescriptor(H,K,Fs)
        ir=ImpulseResponse(Waveform(td,h))
        fir=ir.FirFilter().NormalizeUnityDCGain()
        FirFilter.__init__(self,fir.FilterDescriptor(),fir.FilterTaps())
