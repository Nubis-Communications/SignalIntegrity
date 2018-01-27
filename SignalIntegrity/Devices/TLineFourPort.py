'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
import cmath
import math
# transmission line
#
#           +-----------------------+
#          / \                       \
#         |   |                       |
#   1 ----+-  |     Z    Td           +----- 2
#         |   |                       |
#          \ /                       /
#        +--+-----------------------+--+
#        |                             |
#   3 ---+                             +---- 4
#
#
# is either two or four ports
# ports 1 and 2 are the input and output
# ports 3 and 4 are the outer conductor
# when two ports, ports 3 and 4 are assumed grounded

def TLineFourPort(Zc,gamma,Z0):
    p=(Zc-Z0)/(Zc+Z0)
    a=(1.-3.*p)/(p-3.)
    """
    this calculation for a is the same as:
    a=(Zc-2.*Z0)/(Zc+2.*Z0) or
    a=(Zc/2.-Z0)/(Zc/2.+Z0)
    """
    Y=cmath.exp(-gamma)
    D=2.*(1-Y*Y*a*a)
    S1=(1.-Y*Y*a*a+a*(1.-Y*Y))/D
    S2=(1.-a*a)*Y/D
    S3=((1.-Y*Y*a*a)-a*(1.-Y*Y))/D
    return [[S1,S2,S3,-S2],
            [S2,S1,-S2,S3],
            [S3,-S2,S1,S2],
            [-S2,S3,S2,S1]]