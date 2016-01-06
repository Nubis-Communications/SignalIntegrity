'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
from SignalIntegrity.Devices.TerminationZ import TerminationZ
from numpy import math

def TerminationC(C,f,Z0=None):
    try:
        Z=1./(C*1j*2.*math.pi*f)
    except ZeroDivisionError:
        Z=1e15
    return TerminationZ(Z,Z0)