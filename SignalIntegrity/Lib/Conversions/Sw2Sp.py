"""
Converts pseudo-wave s-parameters to power-wave s-parameters
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

from SignalIntegrity.Lib.Conversions.Z0KHelper import Z0KHelper
from SignalIntegrity.Lib.Conversions.Z0KHelperPW import Z0KHelperPW

def Sw2Sp(Sp,Z0w=None,Z0p=None,Kw=None):
    """Converts power-wave s-parameters to pseudo-wave s-parameters
    @param Sp list of list power-wave based s-parameter matrix to convert
    @param Z0w (optional) the reference impedance of the pseudo-wave based s-parameters (assumed 50 Ohms)
    @param Z0p (optional) the reference impedance of the power-wave based s-parameters (assumed 50 Ohms)
    @param Kw (optional) the scaling factor of the pseudo-wave based s-parameters (assumed to be sqrt(Z0w)
    @return the converted s-parameters in pseudo-waves
    @see Z0KHelper to see how the reference impedance
    and scaling factor are determined for pseudo-waves.
    @see Z0KHelperPW to see the reference impedance
    and scaling factor are determined for power waves.
    """
    if Z0p is None:
        Z0p=Z0w
    (Z0w,Kw)=Z0KHelper((Z0w,Kw),len(Sp))
    (Z0p,Kp)=Z0KHelperPW(Z0p,len(Sp))
    Sp=matrix(Sp)
    Sw=(Kp.getI()*Kw*Z0w.getI()*((Z0w-Z0p.conjugate())+(Z0w+Z0p.conjugate())*Sp)*
        ((Z0w+Z0p)+(Z0w-Z0p)*Sp).getI()*Kp*Kw.getI()*Z0w)
    return Sw
