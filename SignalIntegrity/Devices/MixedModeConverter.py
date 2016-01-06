'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
import math

# Ports 1 2 3 4 are + - D C

# this one has the right definition for differential and common mode voltage
def MixedModeConverterVoltage():
    DF=1.; CF=2.
    return [[0.,0.,DF/2.,CF/2.],
            [0.,0.,-DF/2.,CF/2.],
            [1./DF,-1./DF,0.,0.],
            [1./CF,1./CF,0.,0.]]

# this is an alternate form of the standard mixed-mode converter
def MixedModeConverter():
    DF=math.sqrt(2.0); CF=math.sqrt(2.0)
    return [[0.,0.,DF/2.,CF/2.],
            [0.,0.,-DF/2.,CF/2.],
            [1./DF,-1./DF,0.,0.],
            [1./CF,1./CF,0.,0.]]
