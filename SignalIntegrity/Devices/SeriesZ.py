'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
from SignalIntegrity.Conversions import Z0KHelper

def SeriesZZ0K(Z,Z0=None,K=None):
    (Z0,K)=Z0KHelper((Z0,K),2)
    Z01=Z0.item(0,0)
    Z02=Z0.item(1,1)
    K1=K.item(0,0)
    K2=K.item(1,1)
    D=Z+Z01+Z02
    S11=(Z+Z02-Z01)/D
    S12=(2.*K2/K1*Z01)/D
    S21=(2.*K1/K2*Z02)/D
    S22=(Z+Z01-Z02)/D
    return [[S11,S12],[S21,S22]]

def SeriesZ(Z,Z0=50.):
    return [[Z/(Z+2.*Z0),2.*Z0/(Z+2.*Z0)],[2*Z0/(Z+2.*Z0),Z/(Z+2.*Z0)]]
