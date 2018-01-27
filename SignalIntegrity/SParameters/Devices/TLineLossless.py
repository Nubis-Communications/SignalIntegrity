'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
from SignalIntegrity.SParameters.SParameters import SParameters
import SignalIntegrity.Devices as dev

class TLineLossless(SParameters):
    def __init__(self,f,P,Zc,Td,Z0=50.):
        self.m_Zc=Zc
        self.m_Td=Td
        self.m_P=P
        SParameters.__init__(self,f,None,Z0)
    def __getitem__(self,n):
        if self.m_P==2:
            return dev.TLineTwoPortLossless(self.m_Zc,self.m_Td,self.m_f[n],self.m_Z0)
        elif self.m_P==4:
            return dev.TLineFourPortLossless(self.m_Zc,self.m_Td,self.m_f[n],self.m_Z0)
