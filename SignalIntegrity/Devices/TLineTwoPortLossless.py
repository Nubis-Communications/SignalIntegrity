'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
import math

from TLineTwoPort import TLineTwoPort

def TLineTwoPortLossless(Zc,Td,f,Z0):
    return TLineTwoPort(Zc,1j*2.*math.pi*f*Td,Z0)