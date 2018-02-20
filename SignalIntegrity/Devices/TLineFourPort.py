# Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
# Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
# All Rights Reserved.
#
# Explicit license in accompanying README.txt file.  If you don't have that file
# or do not agree to the terms in that file, then you are not licensed to use
# this material whatsoever.

import cmath


def TLineFourPort(Zc,gamma,Z0):
    """AtPackage si.dev.TLineFourPort
    Ideal Four-port Transmission Line
    @param Zc float or complex characteristic impedance
    @param gamma float or complex propagation constant
    @param Z0 float or complex reference impedance Z0
    @return the s-parameter matrix of a four-port transmission line
    @remark This is actually an oddball construction and should not be confused with a typical differential
    transmission line.\n
    The symbol looks like a two-port transmission line with it's outer conductor exposed as ports on each
    side.\n
    Port 1 is the left side and port 2 is the right side of the two-port transmission line.\n
    Port 3 is the left, exposed, outer conductor and port 4 is the right, exposed outer conductor.\n
    @note this device is functionally equivalent to the two-port transmission line TLineTwoPort() when
    ports 3 and 4 are grounded.
    @todo Make Z0 optional defaulting to 50 Ohms
    @todo fix the ASCII line art.
    """
    """       +-----------------------+
             / \                       \
      1 ----+-  |     Z    Td           +----- 2
             \ /                       /
           +--+-----------------------+--+
           |                             |
      3 ---+                             +---- 4

    ports 1 and 2 are the input and output
    ports 3 and 4 are the outer conductor
    """
    p=(Zc-Z0)/(Zc+Z0)
    a=(1.-3.*p)/(p-3.)
    # pragma: silent exclude
#     this calculation for a is the same as:
#     a=(Zc-2.*Z0)/(Zc+2.*Z0) or
#     a=(Zc/2.-Z0)/(Zc/2.+Z0)
    # pragma: include
    Y=cmath.exp(-gamma)
    D=2.*(1-Y*Y*a*a)
    S1=(1.-Y*Y*a*a+a*(1.-Y*Y))/D
    S2=(1.-a*a)*Y/D
    S3=((1.-Y*Y*a*a)-a*(1.-Y*Y))/D
    return [[S1,S2,S3,-S2],
            [S2,S1,-S2,S3],
            [S3,-S2,S1,S2],
            [-S2,S3,S2,S1]]
