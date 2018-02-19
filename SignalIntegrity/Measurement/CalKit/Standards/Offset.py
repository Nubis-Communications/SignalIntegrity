"""
offset
"""
# Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
# Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
# All Rights Reserved.
# 
# Explicit license in accompanying README.txt file.  If you don't have that file
# or do not agree to the terms in that file, then you are not licensed to use
# this material whatsoever.

import cmath

from SignalIntegrity.SParameters.SParameters import SParameters

class Offset(SParameters):
    """class providing the s-parameters of an offset portion of the various calibration standards
    for a calibration kit."""
    # pragma: silent exclude
    calcZc=False
    # pragma: include
    def __init__(self,fList,offsetDelay,offsetZ0,offsetLoss,f0=1e9):
        """Constructor
        @param fList list of frequencies
        @param offsetDelay (optional) float electrical length of offset in s (defaults to 0 s)
        @param offsetZ0 (optional) float real characteristic impedance of offset (defaults to 50 Ohms)
        @param offsetLoss (optional) float loss due to skin-effect defined in GOhms/s at 1 GHz (defaults to 0).
        @param f0 (optional) float frequency where the offset loss is defined (defaults to 1e9).
        The result is that the class becomes the base-class SParameters with the s-parameters
        of an offset, which is a common portion of a calibration standard.
        """
        data=[]
        Z0=50.
        Zc=offsetZ0
        Td=offsetDelay
        R0=offsetLoss
        L=Td*Zc
        C=Td/Zc
        G=0
        for f in fList:
            R=R0*Td*cmath.sqrt(f/f0)
            Z=R+1j*2*cmath.pi*f*L
            Y=G+1j*2*cmath.pi*f*C
            y=cmath.sqrt(Z*Y)
            # pragma: silent exclude
            try:
                if self.calcZc:
                    Zc=cmath.sqrt(Z/Y)
            except:
                Zc=offsetZ0
            # pragma: include
            rho=(Zc-Z0)/(Zc+Z0)
            D=(1-rho*rho*cmath.exp(-2*y))
            S11=rho*(1-cmath.exp(-2*y))/D
            S21=(1-rho*rho)*cmath.exp(-y)/D
            data.append([[S11,S21],[S21,S11]])
        SParameters.__init__(self,fList,data)