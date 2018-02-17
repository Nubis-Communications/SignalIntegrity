"""
 Ideal Lossless Four-port Transmission Line
"""
# Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
# Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
# All Rights Reserved.
# 
# Explicit license in accompanying README.txt file.  If you don't have that file
# or do not agree to the terms in that file, then you are not licensed to use
# this material whatsoever.

import math
from TLineFourPort import TLineFourPort

## TLineFourPortLossless
#
# @param Zc float or complex characteristic impedance
# @param Td float electrical length (or time delay through the device)
# @param f float frequency
# @param Z0 float or complex characteristic impedance
# @return list of list s-parameters of four-port lossless transmission line
#
# This is actually an oddball construction and should not be confused with a typical differential
# transmission line.
#
# The symbol looks like a two-port transmission line with it's outer conductor exposed as ports on each
# side.
#
# Port 1 is the left side and port 2 is the right side of the two-port transmission line.
#
# Port 3 is the left, exposed, outer conductor and port 4 is the right, exposed outer conductor.
#
# @note this device is functionally equivalent to the two-port ideal lossless transmission line TLineFourPort() when
# ports 3 and 4 are grounded.
#
# todo Make Z0 optional defaulting to 50 Ohms
#
def TLineFourPortLossless(Zc,Td,f,Z0):
    return TLineFourPort(Zc,1j*2.*math.pi*f*Td,Z0)