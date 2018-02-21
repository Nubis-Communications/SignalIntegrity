"""Series capacitance"""
# Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
# Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
# All Rights Reserved.
#
# Explicit license in accompanying README.txt file.  If you don't have that file
# or do not agree to the terms in that file, then you are not licensed to use
# this material whatsoever.

from SignalIntegrity.SParameters.SParameters import SParameters
import SignalIntegrity.Devices as dev

class SeriesC(SParameters):
    """s-parameters of a series capacitance"""
    def __init__(self,f,C,Z0=50.,df=0.,esr=0.):
        """Constructor
        @param f list of float frequencies
        @param C float capacitance
        @param Z0 (optional) float of complex reference impedance (defaults to 50 Ohms)
        @param df (optional) float dissipation factor (or loss-tangent) (defaults to 0)
        @param esr (optional) float effective-series-resistance (defaults to 0)
        @remark The s-parameters are evaluated using the single-frequency device
        SignalIntegrity.Devices.SeriesC
        """
        self.m_C=C
        self.m_df=df
        self.m_esr=esr
        SParameters.__init__(self,f,None,Z0)
    def __getitem__(self,n):
        """overloads [n]
        @return list of list s-parameter matrix for the nth frequency element
        """
        return dev.SeriesC(self.m_C,self.m_f[n],self.m_Z0,self.m_df,self.m_esr)
