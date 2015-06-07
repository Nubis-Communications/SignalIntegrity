from numpy import fft
import math

from SignalIntegrity.TimeDomain.Waveform.TimeDescriptor import TimeDescriptor
from SignalIntegrity.TimeDomain.Waveform.Waveform import Waveform
from SignalIntegrity.TimeDomain.Filters.FilterDescriptor import FilterDescriptor
from SignalIntegrity.TimeDomain.Filters.FirFilter import FirFilter

class ImpulseResponse(Waveform):
    def __init__(self,t,td):
        Waveform.__init__(self,t,td)
    def DelayBy(self,d):
        return ImpulseResponse(self.TimeDescriptor().DelayBy(d),self.Values())
    def FrequencyResponse2(self,fd=None,adjustDelay=False):
        """Produces the frequency response

        Args:
            fd (TimeDescriptor) (optional) the frequency descriptor for the frequency response.
            adjustDelay (bool) whether to adjust the delay.

        Notes:
            All impulse responses are evenly spaced

            whether a frequency descriptor is specified and whether
            to adjust delay determines all possibilities of what can happen.

            fd  ad
            F   F   generic frequency response
            F   T   frequency response with delay adjusted
            T   X   CZT resamples to fd
        """
        from SignalIntegrity.SParameters.FrequencyResponse import FrequencyResponse
        if not fd and not adjustDelay:
            X=fft.fft(self.Values())
            fd=self.TimeDescriptor().FrequencyList()
            return FrequencyResponse(fd,[X[n] for n in range(fd.N+1)]).DelayBy(-self.TimeDescriptor().H)
        if not fd and adjustDelay:
            H=self.TimeDescriptor().H
            Ts=1./self.TimeDescriptor().Fs
            TD=-Ts*(-H/Ts-math.floor(-H/Ts+0.5))
            # TD is the fractional delay of the impulse response
            return self.DelayBy(-TD).FrequencyResponse2().DelayBy(TD)
        if fd:
            return ir.FrequencyResponse2(None,adjustDelay=True).Resample2(fd)
    def Resample2(self,td):
        from SignalIntegrity.SParameters.FrequencyList import EvenlySpacedFrequencyList
        from SignalIntegrity.SParameters.FrequencyResponse import FrequencyResponse
        fr=self.FrequencyResponse2(None,adjustDelay=True)
        fr=fr.Resample(td.FrequencyList())
        return fr.ImpulseResponse(None,adjustDelay=True)
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