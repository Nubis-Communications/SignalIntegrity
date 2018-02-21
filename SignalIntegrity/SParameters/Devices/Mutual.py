"""Mutual inductance"""
# Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
# Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
# All Rights Reserved.
# 
# Explicit license in accompanying README.txt file.  If you don't have that file
# or do not agree to the terms in that file, then you are not licensed to use
# this material whatsoever.

from SignalIntegrity.SParameters.SParameters import SParameters
import SignalIntegrity.Devices as dev

# primary is ports 1 and 2, secondary is ports 3 and 4
# dot on ports 1 and 3
class Mutual(SParameters):
    """s-parameters of a mutual inductance"""
    def __init__(self,f,M,Z0=50.):
        """Constructor
        @param f list of frequencies.
        @param M float mutual inductance.
        @param Z0 (optional) float or complex reference impdedance (defaults to 50 Ohms).
        @remark
        This is a four-port device with no self inductance.\n
        The left leg is from port 1 to 2.\n
        The right leg is from port 3 to 4.\n
        The arrow for the mutual points to ports 1 and 3.\n
        The s-parameters are evaluated using the single-frequency device
        SignalIntegrity.Devices.Mutual
        """
        self.m_M=M
        SParameters.__init__(self,f,None,Z0)
    def __getitem__(self,n):
        """overloads [n]
        @return list of list s-parameter matrix for the nth frequency element
        """
        return dev.Mutual(0.,0.,self.m_M,self.m_f[n],self.m_Z0)