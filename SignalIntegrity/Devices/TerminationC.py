# Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
# Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
# All Rights Reserved.
#
# Explicit license in accompanying README.txt file.  If you don't have that file
# or do not agree to the terms in that file, then you are not licensed to use
# this material whatsoever.

from SignalIntegrity.Devices.TerminationG import TerminationG
from numpy import math

def TerminationC(C,f,Z0=None,df=0.,esr=0.):
    """AtPackage si.dev.TerminationC
    Termination capacitance
    @param C float capacitance
    @param f float frequency
    @param Z0 (optional) float of complex reference impedance (defaults to 50 Ohms)
    @param df (optional) float dissipation factor (or loss-tangent) (defaults to 0)
    @param esr (optional) float effective-series-resistance (defaults to 0)
    @return the list of list s-parameter matrix for a termination capacitance
    """
    G=C*2.*math.pi*f*(1j+df)
    try: G=G+1/esr
    except: pass
    return TerminationG(G,Z0)
