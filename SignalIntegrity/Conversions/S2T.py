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
from numpy import identity

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

