from SignalIntegrity.Devices import Mutual
from SignalIntegrity.Devices import SeriesZ
import math

class FrequencyDependentSParameters():
    def __init__(self,f,Z0=None,K=None):
        self.m_f=f
        self.m_Z0=Z0
        self.m_K=K
    def __getitem__(self,item):
        return self.SParameters(item)
    def __len__(self):
        return len(self.Data)

class SeriesZf(FrequencyDependentSParameters):
    def __init__(self,f,Z,Z0=None,K=None):
        FrequencyDependentSParameters.__init__(self,f,Z0,K)
        self.m_Z=Z
    def SParameters(self,n):
        return SeriesZ(self.m_Z[n],self.m_Z0,self.m_K)

class SeriesLf(FrequencyDependentSParameters):
    def __init__(self,f,L,Z0=None,K=None):
        FrequencyDependentSParameters.__init__(self,f,Z0,K)
        self.m_L=L
    def SParameters(self,n):
        return SeriesZ(self.m_L*1j*2.*math.pi*self.m_f[n],self.m_Z0,self.m_K)

class SeriesCf(FrequencyDependentSParameters):
    def __init__(self,f,C,Z0=None,K=None):
        FrequencyDependentSParameters.__init__(self,f,Z0,K)
        self.m_C=C
    def SParameters(self,n):
        return SeriesZ(1./(self.m_C*1j*2.*math.pi*self.m_f[n]),self.m_Z0,self.m_K)

class Mutualf(FrequencyDependentSParameters):
    def __init__(self,f,M,Z0=None,K=None):
        FrequencyDependentSParameters.__init__(self,f,Z0,K)
        self.m_M=M
    def SParameters(self,n):
        return Mutual(0.,0.,self.m_M,1j*2.*math.pi*self.m_f[n],self.m_Z0)
