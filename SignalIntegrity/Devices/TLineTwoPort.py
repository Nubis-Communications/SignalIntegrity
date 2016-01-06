'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
import cmath

def TLineSE(Zc,gamma,Z0):
    p=(Zc-Z0)/(Zc+Z0)
    L=cmath.exp(-gamma)
    S1=(p*(1.-L*L))/(1.-p*p*L*L)
    S2=((1.-p*p)*L)/(1.-p*p*L*L)
    return [[S1,S2],[S2,S1]]