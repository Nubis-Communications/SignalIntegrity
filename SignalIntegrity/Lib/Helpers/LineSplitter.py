"""
LineSplitter.py
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

def LineSplitter(line):
    sline=line.strip()
    inquote=False
    intoken=False
    acc=''
    tokenList=[]
    for i in range(len(sline)):
        if sline[i]==' ':
            if intoken:
                if not inquote:
                    tokenList.append(acc)
                    acc=''
                else:
                    acc=acc+sline[i]
        elif sline[i]=='\'':
            if inquote:
                inquote=False
                intoken=False
                tokenList.append(acc)
                acc=''
            else:
                intoken=True
                inquote=True
        else:
            if not intoken:
                intoken=True
            acc=acc+sline[i]
    if intoken:
        tokenList.append(acc)
    return tokenList  