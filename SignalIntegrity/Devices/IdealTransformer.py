# Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
# Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
# All Rights Reserved.
#
# Explicit license in accompanying README.txt file.  If you don't have that file
# or do not agree to the terms in that file, then you are not licensed to use
# this material whatsoever.

def IdealTransformer(a=1.):
    """ AtPackage si.dev.IdealTransformer
    Ideal Transformer
    @param a float (optional) turns ratio (defaults to 1)
    @return the s-parameter matrix of an ideal transformer
    Ports 1 and 2 are the primary.

    Ports 3 and 4 are the secondary.

    The dot is on ports 1 and 3.

    a is the turns ratio specified as (secondary/primary) windings
    """
    a=float(a)
    D=a*a+1.
    return [[1./D,a*a/D,a/D,-a/D],
            [a*a/D,1./D,-a/D,a/D],
            [a/D,-a/D,a*a/D,1./D],
            [-a/D,a/D,1./D,a*a/D]]
