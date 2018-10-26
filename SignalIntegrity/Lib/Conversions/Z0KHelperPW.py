"""
 resolves reference impedance and scaling factor for power wave
 defined systems
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
from numpy import matrix
from numpy import diag
from numpy import sqrt

def Z0KHelperPW(Z0,P):
    """Resolves reference impedance and scaling factor from a specification for power waves
    @param Z0 - the reference impedance
    @param P integer number of ports
    @remark
    This very useful function helps resolve all of the possibilities for
    specification of reference impedance and scaling factor under the multitude
    of possibilities on how it can be provided to various conversion functions

    It operates by selecting the best possible choices with the specification
    of the least information.

    If Z0 is not specified, the default 50 Ohms is selected.
    The scaling factor is calculated as sqrt(|Re(Z0)|).
    These are provided in matrix form when needed and complex when needed

    both Z0 and K may be specified as lists, in which case they represent
    port reference impedance and scaling factors
    """
    if Z0 is None:
        Z0=matrix(diag([50.0]*P))
    elif isinstance(Z0,list):
        Z0=matrix(diag([float(i.real)+float(i.imag)*1j for i in Z0]))
    elif isinstance(Z0.real,float) or isinstance(Z0.real,int):
        Z0=matrix(diag([float(Z0.real)+float(Z0.imag)*1j]*P))
    K=sqrt(abs(Z0.real))
    return (Z0,K)