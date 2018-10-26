"""
TerminationG.py
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

from SignalIntegrity.Lib.Devices.TerminationZ import TerminationZ

def TerminationG(G,Z0=50.):
    """TerminationG
    Termination conductance
    @param G float conductance.
    @param Z0 (optional) float of complex reference impedance (defaults to 50 Ohms).
    @return the list of list s-parameter matrix for a termination conductance.
    """
    infinity=1e25
    try: Z = 1.0/G
    except ZeroDivisionError: Z = infinity
    return TerminationZ(Z,Z0)
