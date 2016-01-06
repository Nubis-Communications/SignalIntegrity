'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
from numpy import matrix
from numpy import identity

from Z0KHelper import Z0KHelper

def Z2S(Z,Z0=None,K=None):
    (Z0,K)=Z0KHelper((Z0,K),len(Z))
    Z=matrix(Z)
    return (K.getI()*(Z-Z0)*(Z+Z0).getI()*K).tolist()

