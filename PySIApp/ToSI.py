'''
Created on Oct 29, 2015

@author: peterp
'''
import math

def nextHigher(v,ml):
    ml=sorted(ml)
    exp=math.floor(math.log10(v))
    mul=pow(10.,exp)
    mant=v/mul
    foundit=False
    for m in ml:
        if mant<= m:
            mant = m
            foundit=True
            break
    if not foundit:
        mant=10.
    return mant*mul

def nextLower(v,ml):
    ml = list(reversed(sorted(ml)))
    exp=math.floor(math.log10(v))
    mul=pow(10.,exp)
    mant=v/mul
    foundit=False
    for m in ml:
        if mant >= m:
            mant = m
            foundit=True
            break
    if not foundit:
        mant=0.1
    return mant*mul

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


def ToSI(d,sa=''):

    if d==0.:
        return '0 '+sa

    incPrefixes = ['K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y']
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
        s = "{scaled} {prefix}".format(scaled=scaled, prefix=prefix)
    else:
        s = "{d} ".format(d=d)

    return s+sa
