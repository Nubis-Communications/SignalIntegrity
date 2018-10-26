"""
TerminationZ.py
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

def TerminationZ(Z,Z0=None,K=None):
    """TerminationZ
    Termination impedance
    @param Z float or complex impedance.
    @param Z0 (optional) float of complex reference impedance (defaults to 50 Ohms).
    @param K (optional) float or complex scaling factor (defaults to sqrt(Z0))
    @return the list of list s-parameter matrix for a termination conductance.
    @see Z0KHelper to see how the reference impedance
    and scaling factor are determined.
    """
    (Z0,K)=Z0KHelper((Z0,K),1)
    Z0=Z0.item(0,0)
    Z=float(Z.real)+float(Z.imag)*1j
    return [[(Z-Z0)/(Z+Z0)]]
