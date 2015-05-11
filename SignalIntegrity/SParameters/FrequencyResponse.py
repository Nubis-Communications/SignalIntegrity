from numpy import fft
import math

from SignalIntegrity.SParameters.FrequencyList import *

class FrequencyResponse(object):
    def __init__(self,f,resp):
        if isinstance(f,FrequencyList): self.m_f=f
        elif isinstance(f,list): self.m_f=GenericFrequencyList(f)
        else: self.m_f=f
        self.m_resp=resp
    def Frequency(self):
        return self.m_f
    def Response(self):
        return self.m_resp
    def dB(self):
        return [20.*math.log10(abs(self.m_resp[n])) for n in range(len(self.m_f))]
    def Magnitude(self):
        return [abs(self.m_resp[n]) for n in range(len(self.m_f))]
    def Radians(self):
        return [cmath.phase(self.m_resp[n]) for n in range(len(self.m_f))]
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

class ImpulseResponse(object):
    def __init__(self,t,td):
        self.m_t=t
        self.m_td=td
    def Time(self):
        return self.m_t
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
