"""
TLineFourPortLossless.py
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
from SignalIntegrity.Lib.Devices.TLineFourPort import TLineFourPort

def TLineFourPortLossless(Zc,Td,f,Z0=50.):
    """TLineFourPortLossless
    Ideal Lossless Four-port Transmission Line
    @param Zc float or complex characteristic impedance
    @param Td float electrical length (or time delay through the device)
    @param f float frequency
    @param Z0 (optional) float or complex characteristic impedance (defaults to 50 Ohms)
    @return list of list s-parameters of four-port lossless transmission line
    @remark
    This is actually an oddball construction and should not be confused with a typical differential
    transmission line.\n
    The symbol looks like a two-port transmission line with it's outer conductor exposed as ports on each
    side.\n
    Port 1 is the left side and port 2 is the right side of the two-port transmission line.\n
    Port 3 is the left, exposed, outer conductor and port 4 is the right, exposed outer conductor.\n
    @note this device is functionally equivalent to the two-port ideal lossless transmission line TLineFourPort() when
    ports 3 and 4 are grounded.
    """
    return TLineFourPort(Zc,1j*2.*math.pi*f*Td,Z0)
