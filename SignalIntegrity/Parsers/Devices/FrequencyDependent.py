from SignalIntegrity.Devices import Mutual
from SignalIntegrity.Devices import SeriesZ
from SignalIntegrity.TLines import *

import math

class FrequencyDependentSParameters():
    def __init__(self,f,Z0=50.):
        self.m_f=f
        self.m_Z0=Z0
    def __getitem__(self,item):
        return self.SParameters(item)
    def __len__(self):
        return len(self.Data)

class SeriesZf(FrequencyDependentSParameters):
    def __init__(self,f,Z,Z0=50.):
        FrequencyDependentSParameters.__init__(self,f,Z0)
        self.m_Z=Z
    def SParameters(self,n):
        return SeriesZ(self.m_Z[n],self.m_Z0)

class SeriesLf(FrequencyDependentSParameters):
    def __init__(self,f,L,Z0=50.):
        FrequencyDependentSParameters.__init__(self,f,Z0)
        self.m_L=L
    def SParameters(self,n):
        return SeriesZ(self.m_L*1j*2.*math.pi*self.m_f[n],self.m_Z0)

class SeriesCf(FrequencyDependentSParameters):
    def __init__(self,f,C,Z0=50.):
        FrequencyDependentSParameters.__init__(self,f,Z0)
        self.m_C=C
    def SParameters(self,n):
        return SeriesZ(1./(self.m_C*1j*2.*math.pi*self.m_f[n]),self.m_Z0)

class Mutualf(FrequencyDependentSParameters):
    def __init__(self,f,M,Z0=50.):
        FrequencyDependentSParameters.__init__(self,f,Z0)
        self.m_M=M
    def SParameters(self,n):
        return Mutual(0.,0.,self.m_M,1j*2.*math.pi*self.m_f[n],self.m_Z0)

class Tlinef(FrequencyDependentSParameters):
    def __init__(self,f,P,Zc,Gamma,Z0=50.):
        FrequencyDependentSParameters.__init__(self,f,Z0)
        self.m_Zc=Zc
        self.m_Gamma=Gamma
        self.m_P=P
    def SParameters(self,n):
        if self.m_P==2:
            return TLineSE(self.m_Zc,1j*2.*math.pi*self.m_f[n]*self.m_Gamma,self.m_Z0)
        elif self.m_P==4:
            return TLineFourPort(self.m_Zc,self.m_Gamma,self.m_f[n],self.m_Z0)
