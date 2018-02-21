# Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
# Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
# All Rights Reserved.
# 
# Explicit license in accompanying README.txt file.  If you don't have that file
# or do not agree to the terms in that file, then you are not licensed to use
# this material whatsoever.

import math

from TLineTwoPort import TLineTwoPort

def TLineTwoPortLossless(Zc,Td,f,Z0):
    """TLineTwoPortLossless
    Ideal Lossless Two-port Transmission Line
    @param Zc float or complex characteristic impedance
    @param Td float electrical length (or time delay through the device)
    @param f float frequency
    @param Z0 float or complex characteristic impedance
    @return list of list s-parameters of two-port lossless transmission line
    """
    return TLineTwoPort(Zc,1j*2.*math.pi*f*Td,Z0)