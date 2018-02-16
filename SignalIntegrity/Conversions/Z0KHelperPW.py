"""
 Helps in resolving reference impedance and scaling factor for power wave
 defined systems
"""
# Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
# Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
# All Rights Reserved.
#
# Explicit license in accompanying README.txt file.  If you don't have that file
# or do not agree to the terms in that file, then you are not licensed to use
# this material whatsoever.
from numpy import matrix
from numpy import diag
from numpy import sqrt

## Resolves reference impedance and scaling factor from a specification for power waves
#
# @param Z0K tuple containing (Z0,K) - the reference impedance and scaling factor
# @param P integer number of ports
#
# This very useful function helps resolve all of the possibilities for
# specification of reference impedance and scaling factor under the multitude
# of possibilities on how it can be provided to various conversion functions
#
# It operates by selecting the best possible choices with the specification
# of the least information.
#
# If Z0 is not specified, the default 50 Ohms is selected and if the
# scaling factor is not specified, the default sqrt(Z0) is chosen.
# These are provided in matrix form when needed and complex when needed
#
# both Z0 and K may be specified as lists, in which case they represent
# port reference impedance and scaling factors
#
# @todo Figure out whether these are different from the non-power wave case.
# It seems awfully similar.
def Z0KHelperPW(Z0K,P):
    (Z0,K)=Z0K
    if Z0 is None:
        Z0=matrix(diag([50.0]*P))
    elif isinstance(Z0,list):
        Z0=matrix(diag([float(i.real)+float(i.imag)*1j for i in Z0]))
    elif isinstance(Z0.real,float) or isinstance(Z0.real,int):
        Z0=matrix(diag([float(Z0.real)+float(Z0.imag)*1j]*P))
    if K is None:
        K=sqrt(abs(Z0.real))
    elif isinstance(K,list):
        K=matrix(diag([float(i.real)+float(i.imag)*1j for i in K]))
    elif isinstance(K.real,float) or isinstance(K.real,int):
        K=matrix(diag([float(K.real)+float(K.imag)*1j]*P))
    return (Z0,K)