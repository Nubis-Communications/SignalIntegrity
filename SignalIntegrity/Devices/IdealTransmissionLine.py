# Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
# Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
# All Rights Reserved.
#
# Explicit license in accompanying README.txt file.  If you don't have that file
# or do not agree to the terms in that file, then you are not licensed to use
# this material whatsoever.

import cmath

def IdealTransmissionLine(rho,gamma):
    """IdealTransmissionLine
    Ideal Transmission Line
    @param rho float or complex reflection coefficient
    @param gamma float or complex propagation constant
    @return the s-parameter matrix of an ideal two port transmission line
    rho is defined for a characteristic impedance Zc as (Zc-Z0)/(Zc+Z0)
    """
    L = cmath.exp(-gamma)
    S11=rho*(1.-L*L)/(1.-rho*rho*L*L)
    S21=(1.-rho*rho)*L/(1.-rho*rho*L*L)
    return [[S11,S21],[S21,S11]]