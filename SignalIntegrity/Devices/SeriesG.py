# Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
# Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
# All Rights Reserved.
#
# Explicit license in accompanying README.txt file.  If you don't have that file
# or do not agree to the terms in that file, then you are not licensed to use
# this material whatsoever.

from SignalIntegrity.Devices.SeriesZ import SeriesZ

def SeriesG(G,Z0=50.):
    """AtPackage si.dev.SeriesG
    Series Conductance
    @param G float conductance
    @param Z0 (optional) float of complex reference impedance (defaults to 50 Ohms)
    @return the list of list s-parameter matrix for a series conductance
    @note This device will return the s-paramaters of a series impedance with impedance of 1/G.  If G
    is zero, it uses an impedance equal to 1e25.
    @todo return actual s-parameters of series conductance, even when conductance is zero (as opposed to the weird numerical approximation).
    """
    infinity=1e25
    try: Z = 1.0/G
    except ZeroDivisionError: Z = infinity
    return SeriesZ(Z,Z0)
