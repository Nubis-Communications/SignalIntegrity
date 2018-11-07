"""
LaTeX.py
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

from numpy import empty,sign
import math

def RationalString(val):
    data = ''
    if isinstance(val,int):
        data = str(val)
    elif isinstance(val,float):
        from SignalIntegrity.Lib.Rat import Rat
        from numpy import sign
        sn=sign(val)
        if sn == 0:
            return '0'
        signStr=''
        if sn == -1:
            val=val*-1.
            signStr='-'
        (n,d)=Rat(val)
        if d==1:
            return signStr+str(n)
        elif d<n:
            return signStr+str(val)
        elif d==n:
            return signStr+'1'
        elif ((d<10) and (n<10)):
            return signStr+'\\frac{'+str(n)+'}{'+str(d)+'}'
        # check for square-root of 2
        valsq2=val*math.sqrt(2.)
        (n,d)=Rat(valsq2)
        if d<n:
            return signStr+str(val)
        elif ((d<10) and (n<10)):
            denstr='\\sqrt{2}'
            if d != 1:
                denstr=str(d)+'\\cdot'+denstr
            return signStr+'\\frac{'+str(n)+'}{'+denstr+'}'
        return signStr+str(val)

def Matrix2Text(M):
    if isinstance(M,list):
        R = len(M)
        if isinstance(M[0],list):
            C = len(M[0])
        else:
            M2=[]
            M2.append(M)
            return Matrix2Text(M2)
    else:
        return M
    Result =empty(shape=(R,C)).tolist()
    for r in range(R):
        for c in range(C):
            val = M[r][c]
            data = ''
            if isinstance(val,int):
                data = str(val)
            elif isinstance(val,float):
                data=RationalString(val)
            elif isinstance(val,complex):
                data = str(val.real)+'j'+float(val.imag)
            else:
                data = val
                if data == '':
                    data = '0'
                subscripted=data.split('_')
                if len(subscripted) == 2:
                    if subscripted[1][0] != '{' and subscripted[1][-1] != '}':
                        data=subscripted[0]+'_{'+subscripted[1]+'}'
            Result[r][c] = data
    return Result

def Matrix2LaTeX(M,small=False):
    M = Matrix2Text(M)
    if isinstance(M,list):
        R = len(M)
        if isinstance(M[0],list):
            C = len(M[0])
        else:
            M2=[]
            M2.append(M)
            return Matrix2LaTeX(M2)
    else:
        return ''
    if R==1 and C==1:
        line = ''
    else:
        if small:
            line = '\\left(\\begin{smallmatrix} '
        else:
            line='\\left(\\begin{array}{'+'c'*C+'} '
    for r in range(R):
        if r > 0:
            line = line + ' \\\\ '
        for c in range(C):
            if c>0:
                line=line+' & '
            data = M[r][c]
            line=line+data
    if R==1 and C==1:
        pass
    else:
        if small:
            line = line + ' \\end{smallmatrix}\\right)'
        else:
            line = line + ' \\end{array}\\right)'
    return line

def MatrixMultiply(ML, MR):
    ML = Matrix2Text(ML)
    MR = Matrix2Text(MR)
    rowsResult = len(ML)
    colsResult = len(MR[0])
    Result = empty(shape=(rowsResult, colsResult)).tolist()
    for r in range(rowsResult):
        for c in range(colsResult):
            # result[r][c] = ML[r][i]*MR[i][c] for all i in cols of ML (rows of MR)
            cell = ''
            for i in range(len(MR)):
                prod = ''
                if ML[r][i] == '0' or MR[i][c] == '0':
                    prod = ''
                else:
                    if ML[r][i] == '1':
                        if MR[i][c] == '1':
                            prod = '1'
                        else:
                            prod = MR[i][c]
                    elif MR[i][c] == '1':
                        prod = ML[r][i]
                    else:
                        prod = ML[r][i] + ' \\cdot ' + MR[i][c]
                if cell == '':
                    cell = prod
                else:
                    if prod != '':
                        cell = cell + ' + ' + prod
            if cell == '':
                cell = '0'
            Result[r][c] = cell
    return Result

def SubscriptedVector(v):
    lv=[]
    for node in v:
        if isinstance(node,str):
            if len(node)>1: lv.append(node[0]+'_'+node[1:])
            else: lv.append(node)
        else: lv.append(node)
    return [[i] for i in lv]
