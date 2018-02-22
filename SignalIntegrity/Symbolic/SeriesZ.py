# Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
# Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
# All Rights Reserved.
#
# Explicit license in accompanying README.txt file.  If you don't have that file
# or do not agree to the terms in that file, then you are not licensed to use
# this material whatsoever.

def SeriesZ(Z):
    """symbolic series impedance
    @param Z string impedance
    @return list of list of string s-parameter matrix
    containing LaTeX or ASCII strings for each element.
    @note strings can be any valid LaTeX
    @note this is the symbolic version of SignalIntegrity.Devices.SeriesZ
    """
    return [['\\frac{'+Z+'}{'+Z+'+2\\cdot Z0}','\\frac{2\\cdot Z0}{'+Z+'+2\\cdot Z0}'],
            ['\\frac{2\\cdot Z0}{'+Z+'+2\\cdot Z0}','\\frac{'+Z+'}{'+Z+'+2\\cdot Z0}']]