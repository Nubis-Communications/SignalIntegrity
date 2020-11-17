"""Classical Filter"""

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

from SignalIntegrity.Lib.SParameters.SParameters import SParameters
from SignalIntegrity.Lib.Exception import SignalIntegrityExceptionSParameters

import numpy as np

class ClassicalFilter(SParameters):
    """Classical filter"""
    def __init__(self,f,z,p,k,f0=1.,Z0=50.):
        self.z=z
        self.p=p
        self.k=k
        self.f0=f0
        SParameters.__init__(self,f,None,Z0)
    def _Evaluate(self,f):
        """Evaluate filter
        @param f float frequency
        @return filter evaluated at f
        """
        s=1j*f/self.f0
        D=np.prod([s-self.p[k] for k in range(len(self.p))]); N=np.prod([s-self.z[k] for k in range(len(self.z))])
        return self.k*N/D
    def __getitem__(self,n):
        return [[1.,0],[2.*self._Evaluate(self.m_f[n]),-1.]]

class BesselLowPassFilter(ClassicalFilter):
    """Bessel low pass filter"""
    def __init__(self,f,order,f0,Z0=50.):
        """Constructor
        @param f list of float frequencies
        @param order int filter order
        @param f0 float cutoff frequency (Hz)
        @note This device requires installation of the scipy package
        """
        try:
            from scipy.signal import besselap
        except: raise SignalIntegrityExceptionSParameters('Bessel filters require the scipy package to be installed') # pragma: no cover
        (z,p,k)=besselap(order,'mag')
        # this filter has -3 dB point at w=1 radian
        ClassicalFilter.__init__(self,f,z,p,k,f0,Z0)

class ButterworthLowPassFilter(ClassicalFilter):
    """Butterworth Low pass filter"""
    def __init__(self,f,order,f0,Z0=50.):
        """Constructor
        @param f list of float frequencies
        @param order int filter order
        @param f0 float cutoff frequency (Hz)
        @note This device requires installation of the scipy package
        """
        try:
            from scipy.signal import butter
        except: raise SignalIntegrityExceptionSParameters('Butterworth filters require the scipy package to be installed') # pragma: no cover
        (z,p,k)=butter(order,1.,'lowpass',True,'zpk')
        # this filter has -3 dB point at w=1 radian
        ClassicalFilter.__init__(self,f,z,p,k,f0,Z0)
