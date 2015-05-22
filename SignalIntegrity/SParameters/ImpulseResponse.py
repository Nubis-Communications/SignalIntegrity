from numpy import fft

from SignalIntegrity.TimeDomain.Waveform.TimeDescriptor import TimeDescriptor
from SignalIntegrity.TimeDomain.Waveform.Waveform import Waveform
from SignalIntegrity.TimeDomain.Filters.FilterDescriptor import FilterDescriptor
from SignalIntegrity.TimeDomain.Filters.FirFilter import FirFilter

class ImpulseResponse(Waveform):
    def __init__(self,t,td):
        Waveform.__init__(self,t,td)
    def FrequencyResponse(self):
        from SignalIntegrity.SParameters.FrequencyList import EvenlySpacedFrequencyList
        from SignalIntegrity.SParameters.FrequencyResponse import FrequencyResponse
        td=self.TimeDescriptor()
        v=self.Values()
        K=td.N
        tp=[v[k].real for k in range(K/2)]
        tn=[v[k].real for k in range(K/2,K)]
        y=tp+tn
        Y=fft.fft(y)
        Fs=td.Fs
        N=K/2
        f=EvenlySpacedFrequencyList(Fs/2.,N)
        return FrequencyResponse(f,[Y[n] for n in range(N+1)])
    def FirFilter(self):
        K=len(self)
        td=self.TimeDescriptor()
        return FirFilter(FilterDescriptor(1,-td.H*td.Fs,K-1),self.Values())