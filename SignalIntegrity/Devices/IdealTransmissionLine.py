'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
import cmath

def IdealTransmissionLine(rho,gamma):
    L = cmath.exp(-gamma)
    S11=rho*(1.-L*L)/(1.-rho*rho*L*L)
    S21=(1.-rho*rho)*L/(1.-rho*rho*L*L)
    return [[S11,S21],[S21,S11]]