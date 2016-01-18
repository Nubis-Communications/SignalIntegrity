'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
# ports 1 and 2 are the primary
# ports 3 and 4 are the secondary
# the dot is on ports 1 and 3
# a is the turns ratio (secondary/primary
def IdealTransformer(a=1.):
    a=float(a)
    D=a*a+1.
    return [[1./D,a*a/D,a/D,-a/D],
            [a*a/D,1./D,-a/D,a/D],
            [a/D,-a/D,a*a/D,1./D],
            [-a/D,a/D,1./D,a*a/D]]
