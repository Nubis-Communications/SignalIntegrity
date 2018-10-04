"""
TLineTwoPort.py
"""

# Copyright (c) 2018 Teledyne LeCroy, all rights reserved worldwide.
#
# This file is part of PySI.
#
# PySI is free software: You can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation, either version
# 3 of the License, or any later version.
#
# This program is distrbuted in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <https://www.gnu.org/licenses/>
import cmath

def TLineTwoPort(Zc,gamma,Z0):
    """TLineTwoPort
    Ideal Two-port Transmission Line
    @param Zc float or complex characteristic impedance
    @param gamma float or complex propagation constant
    @param Z0 float or complex reference impedance Z0
    @return the s-parameter matrix of a two-port transmission line
    @todo Make Z0 optional defaulting to 50 Ohms
    """
    p=(Zc-Z0)/(Zc+Z0)
    L=cmath.exp(-gamma)
    S1=(p*(1.-L*L))/(1.-p*p*L*L)
    S2=((1.-p*p)*L)/(1.-p*p*L*L)
    return [[S1,S2],[S2,S1]]