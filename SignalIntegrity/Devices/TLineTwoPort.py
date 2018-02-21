'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
import cmath

def TLineTwoPort(Zc,gamma,Z0):
    """TLineTwoPort
    Ideal Two-port Transmission Line
    @param Zc float or complex characteristic impedance
    @param gamma float or complex propagation constant
    @param Z0 float or complex reference impedance Z0
    @return the s-parameter matrix of a two-port transmission line
    @todo Make Z0 optional defaulting to 50 Ohms
    """
    p=(Zc-Z0)/(Zc+Z0)
    L=cmath.exp(-gamma)
    S1=(p*(1.-L*L))/(1.-p*p*L*L)
    S2=((1.-p*p)*L)/(1.-p*p*L*L)
    return [[S1,S2],[S2,S1]]