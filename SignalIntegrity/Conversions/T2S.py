"""
 T-parameters to s-parameter conversions
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

def T2S(T,lp=None,rp=None):
    """Converts generalized T-parameters to s-parameters
    @param T list of list representing T-parameter matrix to convert
    @param lp (optional) a list of left port numbers
    @param rp (optional) a list of right port numbers
    @note if no list of left and right ports are specified, it assumes that the first
    P/2-1 port are on the left and the remaining ports are on the right
    @remark Supports multi-port devices
    @attention The number of ports must be even
    @attention The port number in the lists are one-based (not zero-based)
    @note The reference impedance and scaling factor associated with the s-parameters
    is unchanged."""
    P=len(T)/2+len(T[0])/2
    if not isinstance(lp,list):
        lp=range(1,P/2+1)
        rp=range(P/2+1,P+1)
    I=identity(P).tolist()
    SL=[]
    SR=[]
    for p in range(P):
        if (p+1) in rp:
            SL.append(I[2*rp.index(p+1)+1])
            SR.append(I[2*rp.index(p+1)])
        else:
            SL.append(T[2*lp.index(p+1)])
            SR.append(T[2*lp.index(p+1)+1])
    return array(matrix(SL)*matrix(SR).getI()).tolist()
