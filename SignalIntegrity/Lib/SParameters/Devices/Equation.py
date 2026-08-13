"""Equation"""

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

from SignalIntegrity.Lib.SParameters.SParameters import SParameters

class Equation(SParameters):
    """base class for two-port s-parameters defined by an equation"""
    def __init__(self,f,eq,Z0=50.):
        self.f=f
        self.eq=eq
        self.m_f=f
        data=[self._Matrix(self._Evaluate(freq)) for freq in f]
        SParameters.__init__(self,f,data,Z0)
    def _Evaluate(self,f):
        """Evaluate equation
        @param f float frequency
        @return equation evaluated at f
        """
        import math,cmath
        import numpy as np
        Fs=2.*self.m_f[-1]
        Ts=1./Fs
        pi=np.pi
        w=2*pi*f
        j=1j
        s=j*w
        z=cmath.exp(s*Ts)
        return eval(self.eq)
    def _Matrix(self,H):
        """the two-port s-parameter matrix built from the evaluated equation value
        @param H complex value of the equation at a frequency
        @return list of list two-port s-parameter matrix
        """
        raise NotImplementedError
