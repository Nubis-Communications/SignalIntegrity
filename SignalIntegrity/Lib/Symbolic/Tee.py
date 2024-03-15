"""
Tee.py
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

from SignalIntegrity.Lib.Helpers.lfrac import lfrac

def Tee(P=3):
    """symbolic Tee
    @param P (optional) integer number of ports (defaults to three)\n
    @return list of list of string s-parameter matrix
    containing LaTeX or ASCII strings for each element.
    @note strings can be any valid LaTeX
    @note this is the symbolic equivalent of SignalIntegrity.Lib.Devices.Tee.Tee
    """
    D=str(P)
    DiagEle='-'+lfrac(str(-(2-P)),D)
    OffDiagEle=lfrac('2',D)
    M=[]
    for r in range(P):
        row=[]
        for c in range(P):
            if r==c:
                ele=DiagEle
            else:
                ele=OffDiagEle
            row.append(ele)
        M.append(row)
    return M

def TeeWithZ2(Z2):
    D='3\\cdot Z0^2+2\\cdot Z0\\cdot '+Z2
    return [[lfrac('-Z0^2',D),lfrac('2\\cdot Z0^2',D),lfrac('2\\cdot Z0^2+2\\cdot Z0\\cdot '+Z2,D)],
        [lfrac('2\\cdot Z0^2',D),lfrac('-Z0^2+2\\cdot Z0\\cdot '+Z2,D),lfrac('2\\cdot Z0^2',D)],
        [lfrac('2\\cdot Z0^2+2\\cdot Z0\\cdot '+Z2,D),lfrac('2\\cdot Z0^2',D),lfrac('-Z0^2',D)]]

def TeeThreePortZ1Z2Z3(Z1,Z2,Z3):
    D='3\\cdot Z0^2+2\\cdot Z0\\cdot\\left('+Z1+'+'+Z2+'+'+Z3+'\\right)+'+Z1+'\\cdot '+Z2+'+'+Z1+'\\cdot '+Z3+'+'+Z2+'\\cdot '+Z3
    return [[lfrac(Z1+'\\cdot '+Z2+'+'+Z1+'\\cdot '+Z3+'+2\\cdot '+Z1+'\\cdot Z0+'+Z2+'\\cdot '+Z3+'-Z0^2',D),lfrac('2\\cdot Z0^2+2\\cdot Z0\\cdot '+Z3,D),lfrac('2\\cdot Z0^2+2\\cdot '+Z2+'\\cdot Z0',D)],
            [lfrac('2\\cdot Z0^2+2\\cdot Z0\\cdot '+Z3,D),lfrac(Z1+'\\cdot '+Z2+'+'+Z2+'\\cdot '+Z3+'+2\\cdot '+Z2+'\\cdot Z0+'+Z1+'\\cdot '+Z3+'-Z0^2',D),lfrac('2\\cdot Z0^2+2\\cdot '+Z1+'\\cdot Z0',D)],
            [lfrac('2\\cdot Z0^2+2\\cdot '+Z2+'\\cdot Z0',D),lfrac('2\\cdot Z0^2+2\\cdot '+Z1+'\\cdot Z0',D),lfrac(Z1+'\\cdot '+Z2+'+'+Z1+'\\cdot '+Z3+'+'+Z2+'\\cdot '+Z3+'+2\\cdot Z0\\cdot '+Z3+'-Z0^2',D)]]

def TeeThreePortSafe(Zt):
    D='3\\cdot \\left('+Zt+'+Z0\\right)'
    return [[lfrac('3\\cdot '+Zt+'-Z0',D),lfrac('2\\cdot Z0',D),lfrac('2\\cdot Z0',D)],
        [lfrac('2\\cdot Z0',D),lfrac('3\\cdot '+Zt+'-Z0',D),lfrac('2\\cdot Z0',D)],
        [lfrac('2\\cdot Z0',D),lfrac('2\\cdot Z0',D),lfrac('3\\cdot '+Zt+'-Z0',D)]]