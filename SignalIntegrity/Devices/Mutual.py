'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
from numpy import matrix
from numpy import array

from SignalIntegrity.Conversions import Y2S

def MutualOld(Ll,Lr,M,s,Z0=None,K=None):
    try:
        F=1.0/(s*(M*M-Ll*Lr))
    except ZeroDivisionError:
        F=1e15
    YM=matrix([[-Lr,Lr,M,-M],[Lr,-Lr,-M,M],[M,-M,-Ll,Ll],[-M,M,Ll,-Ll]])*F
    return array(Y2S(array(YM).tolist(),Z0,K)).tolist()

def Mutual(Ll,Lr,M,s,Z0=None,K=None):
    D=s*s*(Ll*Lr-M*M)+2*Z0*s*(Ll+Lr)+4*Z0*Z0
    S11=(s*s*(Ll*Lr-M*M)+2*s*Ll*Z0)/D
    S12=(2*Z0*(s*Lr+2*Z0))/D
    S13=(2*s*M*Z0)/D
    S14=-S13
    S21=S12
    S22=S11
    S23=S14
    S24=S13
    S31=S13
    S32=S23
    S33=(s*s*(Ll*Lr-M*M)+2*s*Lr*Z0)/D
    S34=2*Z0*(s*Ll+2*Z0)/D
    S41=S14
    S42=S24
    S43=S34
    S44=S33
    return [[S11,S12,S13,S14],
            [S21,S22,S23,S24],
            [S31,S32,S33,S34],
            [S41,S42,S43,S44]]