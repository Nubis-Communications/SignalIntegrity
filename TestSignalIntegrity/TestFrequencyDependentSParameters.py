import unittest
import SignalIntegrity as si
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
    def SParameters(self,n):
        return None

class SeriesZf(FrequencyDependentSParameters):
    def __init__(self,f,Z,Z0=None,K=None):
        FrequencyDependentSParameters.__init__(self,f,Z0,K)
        self.m_Z=Z
    def SParameters(self,n):
        return si.dev.SeriesZ(self.m_Z[n],self.m_Z0,self.m_K)

class SeriesLf(FrequencyDependentSParameters):
    def __init__(self,f,L,Z0=None,K=None):
        FrequencyDependentSParameters.__init__(self,f,Z0,K)
        self.m_L=L
    def SParameters(self,n):
        return si.dev.SeriesZ(self.m_L*1j*2.*math.pi*self.m_f[n],self.m_Z0,self.m_K)

class SeriesCf(FrequencyDependentSParameters):
    def __init__(self,f,C,Z0=None,K=None):
        FrequencyDependentSParameters.__init__(self,f,Z0,K)
        self.m_C=C
    def SParameters(self,n):
        return si.dev.SeriesZ(1./(self.m_C*1j*2.*math.pi*self.m_f[n]),self.m_Z0,self.m_K)

class TestFrequencyDependentSParameters(unittest.TestCase):
    def testSomeExamples(self):
        f=[n*10e6+10e6 for n in range(10)]
        Z=[100. for n in f]
        L=1e-9
        C=1e-12
        testDevice=SeriesZf(f,Z)
        FDS=[]
        FDS.append(SeriesZf(f,Z))
        FDS.append(SeriesLf(f,L))
        FDS.append(SeriesCf(f,C))
        S=[]
        S.append([FDS[0][n] for n in range(len(f))])
        S.append([FDS[1].SParameters(n) for n in range(len(f))])
        S.append([FDS[2].SParameters(n) for n in range(len(f))])
        #print S[0][0]



