"""
ToSI.py
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
import math

def nextHigher(v,ml):
    ml=sorted(ml)
    sign=math.copysign(1.,v)
    v=v*sign
    try:
        exp=math.floor(math.log10(v))
    except ValueError:
        return 0.
    mul=pow(10.,exp)
    mant=v/mul-1e-15
    foundit=False
    for m in ml:
        if mant<= m:
            mant = m
            foundit=True
            break
    if not foundit:
        mant=10.
    return mant*mul*sign

def nextLower(v,ml):
    ml = list(reversed(sorted(ml)))
    sign=math.copysign(1.,v)
    v=v*sign
    try:
        exp=math.floor(math.log10(v))
    except ValueError:
        return 0.
    mul=pow(10.,exp)
    mant=v/mul+1e-15
    foundit=False
    for m in ml:
        if mant >= m:
            mant = m
            foundit=True
            break
    if not foundit:
        mant=0.1
    return mant*mul*sign

def nextHigher125(v):
    return nextHigher(v,[1.,2.,5.])

def nextLower125(v):
    return nextLower(v,[1.,2.,5.])

def nextHigher1245(v):
    return nextHigher(v,[1.,2.,4.,5.])

def nextHigher12458(v):
    return nextHigher(v,[1.,2.,4.,5.,8.])

def nextLower1245(v):
    return nextLower(v,[1.,2.,4.,5.])

def nextLower12458(v):
    return nextLower(v,[1.,2.,4.,5.,8.])

def nextHigherInteger(v):
    return nextHigher(v,[1.+float(m)/100. for m in range(1000)])

def nextLowerInteger(v):
    return nextLower(v,[1.+float(m)/100. for m in range(1000)])

def ToSI(d,sa=''):

    if sa is None:
        sa=''

    if d==0.:
        return '0 '+sa

    incPrefixes = ['k', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y']
    decPrefixes = ['m', 'u', 'n', 'p', 'f', 'a', 'z', 'y']

    degree = int(math.floor(math.log10(math.fabs(d)) / 3))

    prefix = ''

    if degree!=0:
        ds = degree/math.fabs(degree)
        if ds == 1:
            if degree - 1 < len(incPrefixes):
                prefix = incPrefixes[degree - 1]
            else:
                prefix = incPrefixes[-1]
                degree = len(incPrefixes)
        elif ds == -1:
            if -degree - 1 < len(decPrefixes):
                prefix = decPrefixes[-degree - 1]
            else:
                prefix = decPrefixes[-1]
                degree = -len(decPrefixes)

        scaled = float(d * math.pow(1000, -degree))
        s = "{:.12g} {}".format(scaled,prefix)
        if not '.' in s:
            s="{:.12g}.0 {}".format(scaled,prefix)
        #s = "{:.1f} {}".format(scaled,prefix)
    else:
        s = "{:.12g} ".format(d)
        if not '.' in s:
            s = "{:.12g}.0 ".format(d)
        #s = "{:.1f} ".format(d)

    return s+sa

def FromSI(string,unit=None):
    try:
        return float(string)
    except ValueError:
        if unit is not None and unit != '':
            string=string.split(unit)[0]
        try:
            return float(string)
        except ValueError:
            string=string.replace(' ','')
            if len(string) == 0:
                return 0.
            modifier=string[-1]
            therest=string[:-1]
            try:
                man=float(therest)
            except ValueError:
                return None
            Prefixes = ['y','z','a','f','p','n','u','m','',
                        'k','M','G','T','P','E','Z','Y']
            if modifier in Prefixes:
                exp=math.pow(10.,(Prefixes.index(modifier)-Prefixes.index(''))*3)
                return man*exp
    return None

