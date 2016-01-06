'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
from SignalIntegrity.Conversions import Z0KHelper

def TerminationZ(Z,Z0=None,K=None):
    (Z0,K)=Z0KHelper((Z0,K),1)
    Z0=Z0.item(0,0)
    Z=float(Z.real)+float(Z.imag)*1j
    return [[(Z-Z0)/(Z+Z0)]]
