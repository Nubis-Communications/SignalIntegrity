"""
s-parameters to ABCD parameter conversions
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

from numpy import array
from numpy.linalg import inv

from SignalIntegrity.Lib.Conversions.Z0KHelper import Z0KHelper

def S2ABCD(S,Z0=None,K=None):
    """Converts s-parameters to ABCD parameters.
    @param S list of list representing s-parameter matrix to convert
    @param Z0 (optional) float or complex or list of reference impedance (defaults to None).
    @param K (optional) float or complex or list of scaling factor (defaults to None).
    @note
    Supports only two-port devices.\n
    @see Z0KHelper to see how the reference impedance
    and scaling factor are determined."""
    S=array(S)
    (Z0,K)=Z0KHelper((Z0,K),len(S))
    Z01=Z0.item(0,0)
    Z02=Z0.item(1,1)
    K1=K.item(0,0)
    K2=K.item(1,1)
    C11=array([[0,K2],[0,K2/Z02]])
    C12=array([[0,K2],[0,-K2/Z02]])
    C21=array([[K1,0],[-K1/Z01,0]])
    C22=array([[K1,0],[K1/Z01,0]])
    return ((C21+C22.dot(S)).dot(inv(C11+C12.dot(S)))).tolist()
