"""
TLineTwoPortLossless.py
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

import math

from SignalIntegrity.Lib.Devices.TLineTwoPort import TLineTwoPort

def TLineTwoPortLossless(Zc,Td,f,Z0=50.):
    """TLineTwoPortLossless
    Ideal Lossless Two-port Transmission Line
    @param Zc float or complex characteristic impedance
    @param Td float electrical length (or time delay through the device)
    @param f float frequency
    @param Z0 (optional) float or complex characteristic impedance (defaults to 50)
    @return list of list s-parameters of two-port lossless transmission line
    """
    return TLineTwoPort(Zc,1j*2.*math.pi*f*Td,Z0)
