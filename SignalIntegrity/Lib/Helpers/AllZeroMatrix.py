"""
AllZeroMatrix.py
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

def AllZeroMatrix(M):
    for r in range(len(M)):
        for c in range(len(M[r])):
            try:
                if complex(M[r][c]) != 0.:
                    return False
            except ValueError:
                return False
    return True

def ZeroColumns(M):
    zeroColumnList=[]
    for c in range(len(M[0])):
        isAZeroColumn=True
        for r in range(len(M)):
            try:
                if complex(M[r][c]) != 0.:
                    isAZeroColumn=False
                    break
            except ValueError:
                isAZeroColumn=False
                break
        if isAZeroColumn:
            zeroColumnList.append(c)
    return zeroColumnList

def ZeroRows(M):
    zeroRowList=[]
    for r in range(len(M)):
        isAZeroRow=True
        for c in range(len(M[r])):
            try:
                if complex(M[r][c]) != 0.:
                    isAZeroRow=False
                    break
            except ValueError:
                isAZeroRow=False
                break
        if isAZeroRow:
            zeroRowList.append(r)
    return zeroRowList

def NonZeroColumns(M):
    NonZeroColumnList=[]
    for c in range(len(M[0])):
        isAZeroColumn=True
        for r in range(len(M)):
            try:
                if complex(M[r][c]) != 0.:
                    isAZeroColumn=False
                    break
            except ValueError:
                isAZeroColumn=False
                break
        if not isAZeroColumn:
            NonZeroColumnList.append(c)
    return NonZeroColumnList

def NonZeroRows(M):
    NonZeroRowList=[]
    for r in range(len(M)):
        isAZeroRow=True
        for c in range(len(M[r])):
            try:
                if complex(M[r][c]) != 0.:
                    isAZeroRow=False
                    break
            except ValueError:
                isAZeroRow=False
                break
        if not isAZeroRow:
            NonZeroRowList.append(r)
    return NonZeroRowList

