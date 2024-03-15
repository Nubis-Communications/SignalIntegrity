"""one-port inductance"""

# Copyright (c) 2021 Nubis Communications, Inc.
# Copyright (c) 2018-2020 Teledyne LeCroy, Inc.
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

from SignalIntegrity.Lib.Devices.TerminationZ import TerminationZ
from numpy import math

def TerminationL(L,f,Z0=None):
    """Termination (one-port) inductance
    @param L float inductance
    @param f float frequency
    @param Z0 (optional) float of complex reference impedance (defaults to 50 ohms)
    @return the list of list s-parameter matrix for a termination inductance
    """
    return TerminationZ(L*1j*2.*math.pi*f,Z0)