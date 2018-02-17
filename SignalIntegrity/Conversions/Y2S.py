"""
Converts admittance parameters to s-parameters
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

## Converts Y-parameters to s-parameters
#
# @param Y list of list representing Y-parameter matrix to convert
# @param Z0 (optional, defaults to None) the reference impedance
# @param K (optional, defaults to None) scaling factor
#
# Converts Y-parameters to s-parameters
#
# @see Z0KHelper to see how the reference impedance
# and scaling factor are determined.
def Y2S(Y,Z0=None,K=None):
    (Z0,K)=Z0KHelper((Z0,K),len(Y))
    I=matrix(identity(len(Y)))
    Y=matrix(Y)
    return (K.getI()*(I+Z0*Y).getI()*(I-Z0*Y)*K).tolist()
