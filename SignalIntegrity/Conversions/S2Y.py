"""
Converts s-parameters to admittance parameters
"""
# Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
# Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
# All Rights Reserved.
#
# Explicit license in accompanying README.txt file.  If you don't have that file
# or do not agree to the terms in that file, then you are not licensed to use
# this material whatsoever.
from numpy import matrix
from numpy import identity

from Z0KHelper import Z0KHelper

## Converts s-parameters to Y-parameters
# @param S list of list representing s-parameter matrix to convert
# @param Z0 (optional, defaults to None) the reference impedance
# @param K (optional, defaults to None) scaling factor
#
# Converts s-parameters to Y-parameters
#
# @see Z0KHelper to see how the reference impedance
# and scaling factor are determined.
def S2Y(S,Z0=None,K=None):
    (Z0,K)=Z0KHelper((Z0,K),len(S))
    I=matrix(identity(len(S)))
    S=matrix(S)
    return (K*Z0.getI()*(I-S)*(I+S).getI()*K.getI()).tolist()
