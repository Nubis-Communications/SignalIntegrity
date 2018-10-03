# Copyright (c) 2018 Teledyne LeCroy, all rights reserved worldwide.
#
# This file is part of PySI.
#
# PySI is free software: You can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation, either version
# 3 of the License, or any later version.
#
# This program is distrbuted in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <https://www.gnu.org/licenses/>

from numpy import empty

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
                data = str(val)
                if data == '0.0':
                    data = '0'
                elif data == '1.0':
                    data = '1'
                elif data == '-1.0':
                    data = '-1'
                elif data == '0.666666666667':
                    data = '\\frac{2}{3}'
                elif data == '-0.333333333333':
                    data = '-\\frac{1}{3}'
                elif data == '0.707106781187':
                    data = '\\frac{1}{\\sqrt{2}}'
                elif data == '-0.707106781187':
                    data = '-\\frac{1}{\\sqrt{2}}'
                elif data == '-0.5':
                    data = '-\\frac{1}{2}'
                elif data == '0.5':
                    data = '\\frac{1}{2}'
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
