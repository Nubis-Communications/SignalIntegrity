"""series skin-effect resistance"""
# Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
# Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
# All Rights Reserved.
#
# Explicit license in accompanying README.txt file.  If you don't have that file
# or do not agree to the terms in that file, then you are not licensed to use
# this material whatsoever.

from SignalIntegrity.Devices.SeriesZ import SeriesZ
from numpy import math

def SeriesRse(f,Rse,Z0=None):
    """Series Skin-effect Resistance
    @param Rse float resistance specified as Ohms/sqrt(Hz)
    @param f float frequency
    @param Z0 (optional) float of complex reference impedance (defaults to 50 Ohms)
    @return the list of list s-parameter matrix for a series resistance due to skin-effect
    """
    return SeriesZ(Rse*math.sqrt(f),Z0)
