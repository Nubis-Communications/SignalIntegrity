# Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
# Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
# All Rights Reserved.
#
# Explicit license in accompanying README.txt file.  If you don't have that file
# or do not agree to the terms in that file, then you are not licensed to use
# this material whatsoever.

from SignalIntegrity.Devices.TerminationZ import TerminationZ
from numpy import math

def TerminationL(L,f,Z0=None):
    """AtPackage si.dev.TerminationL
    Termination inductance
    @param L float inductance
    @param f float frequency
    @param Z0 (optional) float of complex reference impedance (defaults to 50 Ohms)
    @return the list of list s-parameter matrix for a termination inductance
    """
    return TerminationZ(L*1j*2.*math.pi*f,Z0)