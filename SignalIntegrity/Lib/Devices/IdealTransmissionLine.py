"""
IdealTransmissionLine.py
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

import cmath

def IdealTransmissionLine(rho,gamma):
    """IdealTransmissionLine
    Ideal Transmission Line
    @param rho float or complex reflection coefficient
    @param gamma float or complex propagation constant
    @return the s-parameter matrix of an ideal two port transmission line
    rho is defined for a characteristic impedance Zc as (Zc-Z0)/(Zc+Z0)
    """
    L = cmath.exp(-gamma)
    S11=rho*(1.-L*L)/(1.-rho*rho*L*L)
    S21=(1.-rho*rho)*L/(1.-rho*rho*L*L)
    return [[S11,S21],[S21,S11]]