"""Laplace"""

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

import math

class Laplace(SParameters):
    """Laplace domain equation"""
    def __init__(self,f,eq,Z0=50.):
        self.f=f
        self.eq=eq
        SParameters.__init__(self,f,None,Z0)
    def _Evaluate(self,f):
        """Evaluate equation
        @param f float frequency
        @return laplace equation evaluated at f
        """
        pi=math.pi
        w=2*pi*f
        j=1j
        s=j*w
        return eval(self.eq)
    def __getitem__(self,n):
        return [[1.,0],[2.*self._Evaluate(self.m_f[n]),-1.]]