"""ABCD to s-parameter conversions"""
#  Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
#  Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
#  All Rights Reserved.
# 
#  Explicit license in accompanying README.txt file.  If you don't have that file
#  or do not agree to the terms in that file, then you are not licensed to use
#  this material whatsoever.

from numpy import matrix
from numpy import array

from Z0KHelper import Z0KHelper

def ABCD2S(ABCD,Z0=None,K=None):
    """Converts ABCD parameters to s-parameters.\n
    @param ABCD list of list representing ABCD matrix to convert.
    @param Z0 (optional) float or complex or list of reference impedance (defaults to None).
    @param K (optional) float or complex or list of scaling factor (defaults to None).
    @note
    Supports only two-port devices.\n
    @see Z0KHelper to see how the reference impedance
    and scaling factor are determined.
    """
    (Z0,K)=Z0KHelper((Z0,K),len(ABCD))
    Z01=Z0.item(0,0)
    Z02=Z0.item(1,1)
    K1=K.item(0,0)
    K2=K.item(1,1)
    C11=matrix([[0,0],[1.0/(2.0*K2),Z02/(2.0*K2)]])
    C12=matrix([[1.0/(2.0*K1),-Z01/(2.0*K1)],[0,0]])
    C21=matrix([[0,0],[1.0/(2.0*K2),-Z02/(2.0*K2)]])
    C22=matrix([[1.0/(2.0*K1),Z01/(2.0*K1)],[0,0]])
    return array((C21+C22*ABCD)*((C11+C12*ABCD).getI())).tolist()
