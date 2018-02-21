"""Integer ratios"""
# Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
# Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
# All Rights Reserved.
# 
# Explicit license in accompanying README.txt file.  If you don't have that file
# or do not agree to the terms in that file, then you are not licensed to use
# this material whatsoever.
import math

def Rat(R,tol=0.0001):
    """integer ratio
    @param R float decimal, assumed rational number
    @param tol (optional) float tolerance for result (defaults to 0.0001)
    @return tuple (N,D) where N and D are integers up to ten digits long where
    N/D=R to the tolerance specified
    """
    N=10
    D=[]
    for n in range(N+1):
        D.append(int(math.floor(R)))
        B=R-D[n]
        if B < tol:
            break
        R = 1./B
    N = len(D)-1
    R=(1,0)
    for n in range(N+1):
        R=(R[0]*D[N-n]+R[1],R[0])
    return R