"""
Changes the reference impedance and scaling factor of the s-parameters
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
from numpy import identity

from SignalIntegrity.Lib.Conversions.Z0KHelper import Z0KHelper

def ReferenceImpedance(S,Z0f,Z0i=None,Kf=None,Ki=None):
    """Changes the reference impedance and scaling factor
    @param S s-parameter matrix to convert
    @param Z0f the reference impedance to convert to
    @param Z0i (optional) the reference impedance of the s-parameters (assumed 50 Ohms)
    @param Kf (optional) assumed to be sqrt(Z0f)
    @param Ki (optional) assumed to be sqrt(Z0i)
    @return the converted s-parameters
    @see Z0KHelper to see how the reference impedance
    and scaling factor are determined."""
    (Z0f,Kf)=Z0KHelper((Z0f,Kf),len(S))
    (Z0i,Ki)=Z0KHelper((Z0i,Ki),len(S))
    I=matrix(identity(len(S)))
    p=(matrix(Z0f)-matrix(Z0i))*(matrix(Z0f)+matrix(Z0i)).getI()
    Kf=matrix(Ki)*matrix(Kf).getI()
    S=matrix(S)
    return (Kf*(I-p).getI()*(S-p)*(I-p*S).getI()*(I-p)*Kf.getI()).tolist()
