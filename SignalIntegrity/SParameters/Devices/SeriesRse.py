"""skin-effect resistance"""
# Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
# Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
# All Rights Reserved.
# 
# Explicit license in accompanying README.txt file.  If you don't have that file
# or do not agree to the terms in that file, then you are not licensed to use
# this material whatsoever.

from SignalIntegrity.SParameters.SParameters import SParameters
import SignalIntegrity.Devices as dev

class SeriesRse(SParameters):
    """s-parameters of series skin-effect Resistance"""
    def __init__(self,f,Rse,Z0=50.):
        """Constructor
        @param f list of float frequencies
        @param Rse float resistance specified as Ohms/sqrt(Hz)
        @param Z0 (optional) float of complex reference impedance (defaults to 50 Ohms)
        @note a skin-effect resistance is simply a resistance that is proportional to 
        the square-root of the frequency."""
        self.m_Rse=Rse
        SParameters.__init__(self,f,None,Z0)
    def __getitem__(self,n):
        """overloads [n]
        @return list of list s-parameter matrix for the nth frequency element
        """
        return dev.SeriesRse(self.m_f[n],self.m_Rse,self.m_Z0)