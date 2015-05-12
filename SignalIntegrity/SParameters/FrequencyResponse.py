from numpy import fft
import math
import cmath

from SignalIntegrity.SParameters.FrequencyList import *
from SignalIntegrity.SParameters.ImpulseResponse import *

class FrequencyResponse(object):
    def __init__(self,f,resp):
        self.m_f=FrequencyList(f)
        self.m_resp=resp
    def __getitem__(self,item): return self.m_resp[item]
    def __len__(self): return len(self.m_resp)
    def Frequency(self):
        return self.m_f
    def GHz(self):
        return [self.m_f[n]/1.e9 for n in range(len(self.m_f))]
    def MHz(self):
        return [self.m_f[n]/1.e6 for n in range(len(self.m_f))]
    def KHz(self):
        return [self.m_f[n]/1.e3 for n in range(len(self.m_f))]
    def Response(self):
        return self.m_resp
    def dB(self):
        return [20.*math.log10(abs(self.m_resp[n])) for n in range(len(self.m_f))]
    def Magnitude(self):
        return [abs(self.m_resp[n]) for n in range(len(self.m_f))]
    def Radians(self):
        return [cmath.phase(self.m_resp[n]) for n in range(len(self.m_f))]
    def Degrees(self):
        return [cmath.phase(self.m_resp[n])*180./math.pi for n in range(len(self.m_f))]
    def Real(self):
        return [self.m_resp[n].real for n in range(len(self.m_f))]
    def Imag(self):
        return [self.m_resp[n].imag for n in range(len(self.m_f))]
    def ImpulseResponse(self):
        N=len(self.m_f)-1
        Fs=2.*self.m_f[N]
        K=2*N
        t=[(k-K/2)*1./Fs for k in range(K)]
        tf=[]
        yfp=[self.m_resp[n] for n in range(len(self.m_f))]
        ynp=[self.m_resp[N-nn].conjugate() for nn in range(1,N)]
        y=yfp+ynp
        y[0]=y[0].real
        y[N]=y[N].real
        td=fft.ifft(y)
        tp=[td[k].real for k in range(K/2)]
        tn=[td[k].real for k in range(K/2,K)]
        td=tn+tp
        return ImpulseResponse(t,td)
    def Resample(self,fl,**args):
        from SignalIntegrity.SParameters.ResampledFrequencyResponse import *
        self = ResampledFrequencyResponse(self,fl,**args)
        return self