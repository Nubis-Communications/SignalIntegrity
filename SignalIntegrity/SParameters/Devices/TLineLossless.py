"""Lossless single-ended transmission line"""
# Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
# Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
# All Rights Reserved.
# 
# Explicit license in accompanying README.txt file.  If you don't have that file
# or do not agree to the terms in that file, then you are not licensed to use
# this material whatsoever.

from SignalIntegrity.SParameters.SParameters import SParameters
import SignalIntegrity.Devices as dev

class TLineLossless(SParameters):
    """s-parameters of ideal lossless single-ended transmission line"""
    def __init__(self,f,P,Zc,Td,Z0=50.):
        """Constructor
        @param f list of float frequencies
        @param P integer number of ports (either 2 or 4)
        @param Zc float or complex characteristic impedance
        @param Td float electrical length (propagation time)
        @param Z0 (optional) float or complex reference impedance (defaults to 50 Ohms) 
        @note
        if two ports are specified, SignalIntegrity.Devices.TLineTwoPortLossless
        is used.\n
        Otherwise, if four ports are specified,
        SignalIntegrity.Devices.TLineFourPortLossless is used\n
        """
        self.m_Zc=Zc;   self.m_Td=Td;   self.m_P=P
        SParameters.__init__(self,f,None,Z0)
    def __getitem__(self,n):
        """overloads [n]
        @return list of list s-parameter matrix for the nth frequency element
        """
        if self.m_P==2: return dev.TLineTwoPortLossless(
                self.m_Zc,self.m_Td,self.m_f[n],self.m_Z0)
        elif self.m_P==4: return dev.TLineFourPortLossless(
                self.m_Zc,self.m_Td,self.m_f[n],self.m_Z0)
