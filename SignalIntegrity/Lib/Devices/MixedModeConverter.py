"""
MixedModeConverter.py
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

def MixedModeConverterVoltage():
    """MixedModeConverterVoltage
    Voltage mixed-mode converter
    @return the s-paramater matrix of a voltage mixed-mode converter.
    Ports 1 2 3 4 are + - D C

    this one has the right definition for differential
    and common mode voltage the way we usually understand it meaning
    that the differential voltage is the difference and the common-mode
    voltage is the average of the plus and minus inputs.
    """
    DF=1.; CF=2.
    return [[0.,0.,DF/2.,CF/2.],
            [0.,0.,-DF/2.,CF/2.],
            [1./DF,-1./DF,0.,0.],
            [1./CF,1./CF,0.,0.]]
# pragma: silent exclude

def MixedModeConverter():
    """MixedModeConverter
    Standard mixed-mode converter
    @return the s-paramater matrix of a the standard mixed-mode converter.
    Ports 1 2 3 4 are + - D C

    this one has the right definition for mixed-mode s-parameters.
    """
    DF=math.sqrt(2.0); CF=math.sqrt(2.0)
    return [[0.,0.,DF/2.,CF/2.],
            [0.,0.,-DF/2.,CF/2.],
            [1./DF,-1./DF,0.,0.],
            [1./CF,1./CF,0.,0.]]
# pragma: silent exclude
