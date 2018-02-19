"""
Thru Standard
"""
# Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
# Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
# All Rights Reserved.
# 
# Explicit license in accompanying README.txt file.  If you don't have that file
# or do not agree to the terms in that file, then you are not licensed to use
# this material whatsoever.

from SignalIntegrity.Measurement.CalKit.Standards.Offset import Offset

class ThruStandard(Offset):
    """Class providing the s-parameters of a thru standard as commonly defined
    for a calibration kit."""
    def __init__(self,f,offsetDelay=0.0,offsetZ0=50.0,offsetLoss=0.0,f0=1e9):
        """Constructor
        @param f list of frequencies
        @param offsetDelay (optional) float electrical length of offset in s (defaults to 0 s)
        @param offsetZ0 (optional) float real characteristic impedance of offset (defaults to 50 Ohms)
        @param offsetLoss (optional) float loss due to skin-effect defined in GOhms/s at 1 GHz (defaults to 0).
        @param f0 (optional) float frequency where the offset loss is defined (defaults to 1e9).
        The result is that the class becomes the base-class SParameters with the s-parameters
        of a thru standard."""
        Offset.__init__(self,f,offsetDelay,offsetZ0,offsetLoss,f0)
