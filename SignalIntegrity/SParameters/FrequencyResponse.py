from numpy import fft
import math
import cmath

from SignalIntegrity.SParameters.FrequencyList import FrequencyList
from SignalIntegrity.SParameters.FrequencyList import EvenlySpacedFrequencyList
from SignalIntegrity.SParameters.FrequencyList import GenericFrequencyList
from SignalIntegrity.SParameters.ImpulseResponse import ImpulseResponse
from SignalIntegrity.TimeDomain.Waveform.TimeDescriptor import TimeDescriptor

class FrequencyResponse(object):
    def __init__(self,f=None,resp=None):
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
    def ReadFromFile(self,fileName):
        with open(fileName,"rU") as f:
            data=f.readlines()
        if data[0].strip('\n')=='EvenlySpaced':
            N = int(str(data[1]))
            Fe = float(str(data[2]))
            resp=[complex(v) for v in data[3:]]
            self.m_f=EvenlySpacedFrequencyList(Fe,N)
            self.m_resp=resp
        else:
            frl=[line.split(' ') for line in data[0:]]
            f=[float(fr[0]) for fr in frl]
            resp=[complex(fr[1] for fr in frl)]
            self.m_f=GenericFrequencyList(f)
        return self
    def WriteToFile(self,fileName):
        fl=self.FrequencyList()
        with open(fileName,"w") as f:
            if fl.CheckEvenlySpaced():
                f.write('EvenlySpaced\n')
                f.write(str(fl.N)+'\n')
                f.write(str(fl.Fe)+'\n')
                for v in self.Response():
                    f.write(str(v)+'\n')
            else:
                for n in len(fl):
                    f.write(str(fl[n])+' '+str(self.Response()[n])+'\n')
        return self
    def __eq__(self,other):
        if self.FrequencyList() != other.FrequencyList():
            return False
        if len(self.Response()) != len(other.Response()):
            return False
        for k in range(len(self.Response())):
            if abs(self.Response()[k] - other.Response()[k]) > 1e-5:
                return False
        return True
    def __ne__(self,other):
        return not self == other

