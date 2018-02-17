"""
Converts s-parameters to T-parameters
"""
#  Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
#  Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
#  All Rights Reserved.
# 
#  Explicit license in accompanying README.txt file.  If you don't have that file
#  or do not agree to the terms in that file, then you are not licensed to use
#  this material whatsoever.

from numpy import matrix
from numpy import array
from numpy import identity

##
# @param S list of list representing s-parameter matrix to convert
# @param lp (optional) a list of left port numbers
# @param rp (optional) a list of right port numbers
#
# Converts s-parameters to generalized T-parameters
#
# if no list of left and right ports are specified, it assumes that the first
# P/2-1 port are on the left and the remaining ports are on the right
#
# Supports multi-port devices
#
# @attention The number of ports must be even
# @attention The port number in the lists are one-based (not zero-based)
#
# The reference impedance and scaling factor associated with the s-parameters
# is unchanged.
def S2T(S,lp=None,rp=None):
    P=len(S)
    if not isinstance(lp,list):
        lp=range(1,P/2+1)
        rp=range(P/2+1,P+1)
    I=identity(P).tolist()
    TL=[]
    for r in range(len(lp)):
        TL.append(S[lp[r]-1])
        TL.append(I[lp[r]-1])
    TR=[]
    for r in range(len(rp)):
        TR.append(I[rp[r]-1])
        TR.append(S[rp[r]-1])
    return array(matrix(TL)*matrix(TR).getI()).tolist()
