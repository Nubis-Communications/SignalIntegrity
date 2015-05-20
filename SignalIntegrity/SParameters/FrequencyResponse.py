from numpy import fft
import math
import cmath

from SignalIntegrity.SParameters.FrequencyList import FrequencyList
from SignalIntegrity.SParameters.ImpulseResponse import ImpulseResponse
from SignalIntegrity.Waveform.TimeDescriptor import TimeDescriptor

class FrequencyResponse(object):
    def __init__(self,f,resp):
        self.m_f=FrequencyList(f)
        self.m_resp=resp
    def __getitem__(self,item): return self.m_resp[item]
    def __len__(self): return len(self.m_resp)
    def FrequencyList(self):
        return self.m_f
    def Frequencies(self,unit=None):
        return self.m_f.Frequencies(unit)
    def Response(self,unit=None):
        if unit==None:
            return self.m_resp
        elif unit =='dB':
            return [20.*math.log10(abs(self.m_resp[n])) for n in range(len(self.m_f))]
        elif unit == 'mag':
            return [abs(self.m_resp[n]) for n in range(len(self.m_f))]
        elif unit == 'rad':
            return [cmath.phase(self.m_resp[n]) for n in range(len(self.m_f))]
        elif unit == 'deg':
            return [cmath.phase(self.m_resp[n])*180./math.pi for n in range(len(self.m_f))]
        elif unit == 'real':
            return [self.m_resp[n].real for n in range(len(self.m_f))]
        elif unit == 'imag':
            return [self.m_resp[n].imag for n in range(len(self.m_f))]
    def ImpulseResponse(self,td=None,**args):
        from SignalIntegrity.SParameters.ResampledFrequencyResponse import ResampledFrequencyResponse
        if not td is None:
            fr=ResampledFrequencyResponse(self,td.FrequencyList(),**args)
        else:
            fr=self
        adjustDelay = args['adjustDelay'] if 'adjustDelay' in args else False
        fd=fr.FrequencyList()
        td=fd.TimeDescriptor()
        TD = cmath.phase(self[-1])/(2.*math.pi*fd[-1]) if adjustDelay else 0.
        td.DelayBy(-TD)
        N=fd.N
        K=2*N
        yfp=[fr.m_resp[n]*cmath.exp(-1j*2.*math.pi*fd[n]*TD) for n in range(N+1)]
        ynp=[yfp[N-nn].conjugate() for nn in range(1,N)]
        y=yfp+ynp
        y[0]=y[0].real
        y[N]=y[N].real
        Y=fft.ifft(y)
        tp=[Y[k].real for k in range(K/2)]
        tn=[Y[k].real for k in range(K/2,K)]
        Y=tn+tp
        return ImpulseResponse(td,Y)
    def Resample(self,fl,**args):
        from SignalIntegrity.SParameters.ResampledFrequencyResponse import ResampledFrequencyResponse
        self = ResampledFrequencyResponse(self,fl,**args)
        return self