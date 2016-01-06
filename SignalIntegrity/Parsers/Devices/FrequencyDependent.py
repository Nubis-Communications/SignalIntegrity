'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
from SignalIntegrity.Devices import Mutual
from SignalIntegrity.Devices import SeriesZ
from SignalIntegrity.SParameters.SParameters import SParameters

import math

class SeriesZf(SParameters):
    def __init__(self,f,Z,Z0=50.):
        self.m_Z=Z
        SParameters.__init__(self,f,None,Z0)
    def __getitem__(self,n):
        return SeriesZ(self.m_Z[n],self.m_Z0)

##class SeriesLf(SParameters):
##    def __init__(self,f,L,Z0=50.):
##        SParameters.__init__(self,f,None,Z0)
##        self.m_L=L
##    def __getitem__(self,n):
##        return SeriesZ(self.m_L*1j*2.*math.pi*self.m_f[n],self.m_Z0)
##
##class SeriesCf(SParameters):
##    def __init__(self,f,C,Z0=50.):
##        SParameters.__init__(self,f,None,Z0)
##        self.m_C=C
##    def __getitem__(self,n):
##        return SeriesZ(1./(self.m_C*1j*2.*math.pi*self.m_f[n]),self.m_Z0)
##
##class Mutualf(SParameters):
##    def __init__(self,f,M,Z0=50.):
##        SParameters.__init__(self,f,None,Z0)
##        self.m_M=M
##    def __getitem__(self,n):
##        return Mutual(0.,0.,self.m_M,1j*2.*math.pi*self.m_f[n],self.m_Z0)
##
##class Tlinef(SParameters):
##    def __init__(self,f,P,Zc,Gamma,Z0=50.):
##        SParameters.__init__(self,f,None,Z0)
##        self.m_Zc=Zc
##        self.m_Gamma=Gamma
##        self.m_P=P
##    def __getitem__(self,n):
##        if self.m_P==2:
##            return TLineSE(self.m_Zc,1j*2.*math.pi*self.m_f[n]*self.m_Gamma,self.m_Z0)
##        elif self.m_P==4:
##            return TLineFourPort(self.m_Zc,self.m_Gamma,self.m_f[n],self.m_Z0)
