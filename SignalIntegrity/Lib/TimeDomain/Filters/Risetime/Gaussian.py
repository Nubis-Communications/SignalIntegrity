"""
Gaussian.py
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
from SignalIntegrity.Lib.TimeDomain.Filters.FilterDescriptor import FilterDescriptor
from SignalIntegrity.Lib.FrequencyDomain.FrequencyList import EvenlySpacedFrequencyList
from SignalIntegrity.Lib.FrequencyDomain.FrequencyResponse import FrequencyResponse

class Gaussian(FirFilter):
    """
    Gaussian COM based FIR filter that, when convolved with step, provides
    the risetime specified at the given sample rate.
    """
    a2080=1.683244 # hardcoded relationship that produces 20-80 risetime
    a1090=2.563103 # hardcoded relationship that produces 10-90 risetime
    def __init__(self,rt,Fs,is1090=True):
        """constructor
        @param rt float risetime desired.
        @param Fs float sample rate
        @param is1090 boolean (optional, defaults to True) whether 10-90 risetime
        is specified.  Otherwise 20-80 risetime is used.
        """
        a=self.a1090 if is1090 else self.a2080
        impulse_response_length = rt*1.2*10*2
        if impulse_response_length == 0:
            FirFilter.__init__(self,FilterDescriptor(1,0,0),[1])
        else:
            import numpy as np
            frequency_resolution = 1/impulse_response_length
            frequency_points = np.ceil(Fs/2/frequency_resolution)-1
            fd=EvenlySpacedFrequencyList(Fs/2,frequency_points)
            v=[np.exp(-2*(np.pi*f*rt/a)**2) for f in fd]
            fr=FrequencyResponse(fd,v)
            ir=fr.ImpulseResponse()
            fir=ir.FirFilter().NormalizeUnityDCGain()
            FirFilter.__init__(self,fir.FilterDescriptor(),fir.FilterTaps())
