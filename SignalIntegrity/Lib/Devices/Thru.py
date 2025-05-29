"""
Thru.py
"""

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

def Thru(ports=2):
    """Thru
    Thru device
    @param ports integer optional (defaults to 2) number of ports
    @returns the list of list s-parameter matrix of an ideal thru.
    @remark The number of ports must be even
    @remark ports 1 to P//2 are on the left and ports P//2+1 to P are on the right.
    Thru connections are made between each left and corresponding right port.
    """
    if (ports < 2) or (ports//2*2 != ports):
        raise ValueError('ports must be even for thru devices')
    S=[[0. for _ in range(ports)] for _ in range(ports)]
    for p in range(ports//2):
        S[p][ports//2+p]=1.
        S[ports//2+p][p]=1.
    return S