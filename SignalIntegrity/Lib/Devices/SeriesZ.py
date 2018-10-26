"""
SeriesZ.py
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
from SignalIntegrity.Lib.Conversions import Z0KHelper

# pragma: silent exclude
def SeriesZZ0K(Z,Z0=None,K=None):
    (Z0,K)=Z0KHelper((Z0,K),2)
    Z01=Z0.item(0,0)
    Z02=Z0.item(1,1)
    K1=K.item(0,0)
    K2=K.item(1,1)
    D=Z+Z01+Z02
    S11=(Z+Z02-Z01)/D
    S12=(2.*K2/K1*Z01)/D
    S21=(2.*K1/K2*Z02)/D
    S22=(Z+Z01-Z02)/D
    return [[S11,S12],[S21,S22]]
# pragma: include

def SeriesZ(Z,Z0=50.):
    """SeriesZ
    Series Impedance
    @param Z float or complex impedance
    @param Z0 (optional) float of complex reference impedance (defaults to 50 Ohms)
    @return the list of list s-parameter matrix for a series impedance
    """
    return [[Z/(Z+2.*Z0),2.*Z0/(Z+2.*Z0)],[2*Z0/(Z+2.*Z0),Z/(Z+2.*Z0)]]
