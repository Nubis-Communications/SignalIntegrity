# Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
# Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
# All Rights Reserved.
#
# Explicit license in accompanying README.txt file.  If you don't have that file
# or do not agree to the terms in that file, then you are not licensed to use
# this material whatsoever.

import math

def MixedModeConverterVoltage():
    """MixedModeConverterVoltage
    Voltage mixed-mode converter
    @return the s-paramater matrix of a voltage mixed-mode converter.
    Ports 1 2 3 4 are + - D C

    this one has the right definition for differential
    and common mode voltage the way we usually understand it meaning
    that the differential voltage is the difference and the common-mode
    voltage is the average of the plus and minus inputs.
    """
    DF=1.; CF=2.
    return [[0.,0.,DF/2.,CF/2.],
            [0.,0.,-DF/2.,CF/2.],
            [1./DF,-1./DF,0.,0.],
            [1./CF,1./CF,0.,0.]]
# pragma: silent exclude

def MixedModeConverter():
    """MixedModeConverter
    Standard mixed-mode converter
    @return the s-paramater matrix of a the standard mixed-mode converter.
    Ports 1 2 3 4 are + - D C

    this one has the right definition for mixed-mode s-parameters.
    """
    DF=math.sqrt(2.0); CF=math.sqrt(2.0)
    return [[0.,0.,DF/2.,CF/2.],
            [0.,0.,-DF/2.,CF/2.],
            [1./DF,-1./DF,0.,0.],
            [1./CF,1./CF,0.,0.]]
# pragma: silent exclude
