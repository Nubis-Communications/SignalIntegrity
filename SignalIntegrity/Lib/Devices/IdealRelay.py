"""
IdealRelay.py
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

def IdealRelay(ports,position,termination='open',Z0=50.):
    """IdealRelay
    An ideal relay with a given number of ports, where the common is always the last port.
    I.e. for a given number ports P, port P is always the common connection and ports 1 through
    P-1 are the throws of the relay (the ports that get connected to the common) in port order.
    The position value ranges from 0 to P-1, where 0 says that none of the throws are connected to
    the common, and a value from 1 to P-1 indicates the throw port connected to the common.
    Valid terminations are the string 'open', or a number indicating the impedance of the unconnected
    port.  This impedance is also applied to the common, when no ports are connected.
    @param ports int number of ports in the relay (including the common).
    @parem position int number from 0 to ports-1 indicating the relay position.
    @param float or string (optional, defaults to 'open' termination applied to unconnected ports.
    @param float (optional, defaults to 50) reference impedance.
    @returns the list of list s-parameter matrix of the ideal relay in the position specified.
    """
    if termination == 'open': rho=1.
    else: rho=TerminationZ(termination,Z0)[0][0]
    S=[[rho if r==c else 0 for c in range(ports)] for r in range(ports)]
    if 0 < position < ports:
        S[position-1][position-1] = 0;  S[position-1][ports-1] = 1.
        S[ports-1][position-1] =    1.; S[ports-1][ports-1] =    0
    return S
