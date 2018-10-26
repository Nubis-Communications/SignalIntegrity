"""
Mutual.py
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

from numpy import matrix
from numpy import array
import math

from SignalIntegrity.Lib.Conversions import Y2S

# old definition
def MutualOld(Ll,Lr,M,f,Z0=None,K=None):
    s=1j*2.*math.pi*f
    try:
        F=1.0/(s*(M*M-Ll*Lr))
    except ZeroDivisionError:
        F=1e15
    YM=matrix([[-Lr,Lr,M,-M],[Lr,-Lr,-M,M],[M,-M,-Ll,Ll],[-M,M,Ll,-Ll]])*F
    return array(Y2S(array(YM).tolist(),Z0,K)).tolist()

def Mutual(Ll,Lr,M,f,Z0=None,K=None):
    """Mutual
    Mutual Inductance
    @param Ll float self inductance of left leg
    @param Lr float self inductance of right leg
    @param M float mutual inductance between legs
    @param f float frequency
    @param Z0 (optional) float or complex reference impedance (assumed 50 Ohms)
    @param K (optional) float or complex scaling factor (actually unused).
    @return list of list representing s-parameter matrix of a mutual inductance
    @remark The device is four port.\n
    The left leg is from port 1 to 2.\n
    The right leg is from port 3 to 4.\n
    The arrow for the mutual points to ports 1 and 3.\n
    @todo use Z0KHelper to resolve reference impedance and scaling factor.  Currently K is not used.
    @todo remove old mutual inductance code
    """
    s=1j*2.*math.pi*f
    D=s*s*(Ll*Lr-M*M)+2*Z0*s*(Ll+Lr)+4*Z0*Z0
    S11=(s*s*(Ll*Lr-M*M)+2*s*Ll*Z0)/D
    S12=(2*Z0*(s*Lr+2*Z0))/D
    S13=(2*s*M*Z0)/D
    S14=-S13
    S21=S12
    S22=S11
    S23=S14
    S24=S13
    S31=S13
    S32=S23
    S33=(s*s*(Ll*Lr-M*M)+2*s*Lr*Z0)/D
    S34=2*Z0*(s*Ll+2*Z0)/D
    S41=S14
    S42=S24
    S43=S34
    S44=S33
    return [[S11,S12,S13,S14],
            [S21,S22,S23,S24],
            [S31,S32,S33,S34],
            [S41,S42,S43,S44]]