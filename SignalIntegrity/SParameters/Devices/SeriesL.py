"""series inductance"""
# Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
# Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
# All Rights Reserved.
# 
# Explicit license in accompanying README.txt file.  If you don't have that file
# or do not agree to the terms in that file, then you are not licensed to use
# this material whatsoever.
from SignalIntegrity.SParameters.SParameters import SParameters
import SignalIntegrity.Devices as dev

class SeriesL(SParameters):
    """s-parameters of a series inductance"""
    def __init__(self,f,L,Z0=50.):
        """Constructor
        @param f list of float frequencies
        @param L float inductance
        @param Z0 (optional) float of complex reference impedance (defaults to 50 Ohms)
        """
        self.m_L=L
        SParameters.__init__(self,f,None,Z0)
    def __getitem__(self,n):
        """overloads [n]
        @return list of list s-parameter matrix for the nth frequency element
        """
        return dev.SeriesL(self.m_L,self.m_f[n],self.m_Z0)
