"""
RaisedCosineRisetimeFilter.py
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

from SignalIntegrity.Lib.SParameters.Devices.Equalizer import FFE
from SignalIntegrity.Lib.TimeDomain.Filters.Risetime.RaisedCosine import RaisedCosine

class RaisedCosineRisetimeFilter(FFE):
    """
    Raised cosine FIR filter that, when convolved with step, provides
    the risetime specified at the given sample rate.
    """
    def __init__(self,f,rt,is1090=True,Z0=50.):
        """constructor
        @param rt float risetime desired.
        @param Fs float sample rate
        @param is1090 boolean (optional, defaults to True) whether 10-90 risetime
        is specified.  Otherwise 20-80 risetime is used.
        @param Z0 float (optional, defaults to 50) reference impedance

        The s-parameters are for a two-port device that is "amplifier-like", meaning it has infinite
        input impedance, zero output impedance, the impulse response forms s21, and has infinite reverse
        isolation.
        """
        Fs=f[-1]*2.
        fir=RaisedCosine(rt,Fs,is1090)
        FFE.__init__(self,f,1./Fs,fir.FilterTaps(),fir.FilterDescriptor().D,Z0)