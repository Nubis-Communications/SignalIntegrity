"""
Tee.py
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

from numpy import empty

def Tee(P=None):
    """Tee
    Tee device
    @param P (optional) integer number of ports for the tee (default is three).
    @return the list of list s-parameter matrix for a tee connection.
    @remark A tee connection is a dot in a schematic.
    """
    if P is None: P=3
    return [[(2.-P)/P if r==c else 2./P for c in range(P)] for r in range(P)]
# pragma: silent exclude

def TeeThreePortSafe(Z,Z0=50.):
    D=3*(Z+Z0)
    DiagEle=(3*Z-Z0)/D
    OffDiagEle=2*Z0/D
    return [[DiagEle,OffDiagEle,OffDiagEle],
            [OffDiagEle,DiagEle,OffDiagEle],
            [OffDiagEle,OffDiagEle,DiagEle]]
