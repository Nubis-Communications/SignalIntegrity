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
from numpy import math

class TLine(SParameters):
    def __init__(self,f,P,Zc,Gamma,Z0=50.):
        self.m_Zc=Zc
        self.m_Gamma=Gamma
        self.m_P=P
        SParameters.__init__(self,f,None,Z0)
    def __getitem__(self,n):
        if self.m_P==2:
            return dev.TLineTwoPort(self.m_Zc,self.m_Gamma,self.m_f[n],self.m_Z0)
        elif self.m_P==4:
            return dev.TLineFourPort(self.m_Zc,self.m_Gamma,self.m_f[n],self.m_Z0)
