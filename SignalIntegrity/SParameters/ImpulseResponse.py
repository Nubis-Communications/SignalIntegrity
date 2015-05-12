from numpy import fft

from SignalIntegrity.SParameters.FrequencyList import *
from SignalIntegrity.SParameters.FrequencyResponse import *

class ImpulseResponse(object):
    def __init__(self,t,td):
        self.m_t=t
        self.m_td=td
    def __getitem__(self,item): return self.m_td[item]
    def __len__(self): return len(self.m_td)
    def Time(self):
        return self.m_t
    def ps(self):
        return [self.m_t[k]/1.e-12 for k in range(len(self.m_t))]
    def ns(self):
        return [self.m_t[k]/1.e-9 for k in range(len(self.m_t))]
    def us(self):
        return [self.m_t[k]/1.e-6 for k in range(len(self.m_t))]
    def ms(self):
        return [self.m_t[k]/1.e-3 for k in range(len(self.m_t))]
    def Response(self):
        return self.m_td
    def FrequencyResponse(self):
        K=len(self.m_t)
        tp=[self.m_td[k].real for k in range(K/2)]
        tn=[self.m_td[k].real for k in range(K/2,K)]
        y=tp+tn
        Y=fft.fft(y)
        Fs=1./self.m_t[1]-self.m_t[0]
        N=K/2
        f=EvenlySpacedFrequencyList(Fs/2.,N)
        return FrequencyResponse(f,[Y[n] for n in range(N+1)])