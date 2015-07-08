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
    def FrequencyResponse(self,fd=None,adjustLength=True):
        """Produces the frequency response

        Args:
            fd (FrequencyDescriptor) (optional) the desired frequency descriptor.
            adjustLength (bool) (optional) whether to adjust the length.
                defaults to True

        Notes:
            All impulse responses are evenly spaced

            whether a frequency descriptor is specified and whether
            to adjust length determines all possibilities of what can happen.

            fd  al
            F   F   generic frequency response
            F   T   frequency response with length adjusted
            T   X   CZT resamples to fd (length is adjusted first)
        """
        from SignalIntegrity.FrequencyDomain.FrequencyResponse import FrequencyResponse
        if not fd and not adjustLength:
            X=fft.fft(self.Values())
            fd=self.TimeDescriptor().FrequencyList()
            return FrequencyResponse(fd,[X[n] for n in range(fd.N+1)]).\
                _DelayBy(self.TimeDescriptor().H)
        if not fd and adjustLength:
            return self._AdjustLength().FrequencyResponse(None,adjustLength=False)
        if fd:
            return self.FrequencyResponse().Resample(fd)
    def _AdjustLength(self):
        td = self.TimeDescriptor()
        PositivePoints = int(max(0,math.floor(td.H*td.Fs+td.N+0.5)))
        NegativePoints = int(max(0,math.floor(-td.H*td.Fs+0.5)))
        P=max(PositivePoints,NegativePoints)*2
        return self._Pad(P)
    def _Pad(self,P):
        """Pads the impulse response

        Args:
            P (int) the desired number of time points.

        Notes:
            P must be even - not checked - it must add equal points to the left
            and right of the impulse response.
            K is the number of points in the selfs frequency response

            if P==K, the original response is returned
            if P<K, the response is truncated to P time points
            if P>K, the response is zero padded to P time points
        """
        K=len(self)
        if P==K:
            x = self.Values()
        elif P<K:
            x=[self.Values()[k] for k in range((K-P)/2,K-(K-P)/2)]
        else:
            x=[0 for p in range((P-K)/2)]
            x=x+self.Values()+x
        td = self.TimeDescriptor()
        return ImpulseResponse(TimeDescriptor(td.H-(P-K)/2./td.Fs,P,td.Fs),x)
    def _FractionalDelayTime(self):
        td=self.TimeDescriptor()
        TD=-(-td.H*td.Fs-math.floor(-td.H*td.Fs+0.5))/td.Fs
        return TD
    def Resample(self,td):
        fr=self.FrequencyResponse()
        return fr.ImpulseResponse(td)
    def TrimToThreshold(self,threshold):
        x=self.Values()
        td=self.TimeDescriptor()
        maxabsx=max(self.Values('abs'))
        minv=maxabsx*threshold
        for k in range(len(x)):
            if abs(x[k]) >= minv:
                startidx = k
                break
        for k in range(len(x)):
            ki = len(x)-1-k
            if abs(x[ki]) >= minv:
                endidx = ki
                break
        if (endidx-startidx+1)/2*2 != endidx-startidx+1:
            # the result would not have an even number of points
            if endidx < len(x)-1:
                # include a point at the end if possible
                endidx = endidx + 1
            elif startidx > 0:
                # include a point at the beginning if possible
                startidx = startidx - 1
            else:
                # append a zero to the end and calculate number of
                # points with endidx+1
                return ImpulseResponse(TimeDescriptor(td[startidx],
                    (endidx+1)-startidx+1,td.Fs),
                    [x[k] for k in range(startidx,endidx+1)]+[0.])
        return ImpulseResponse(TimeDescriptor(td[startidx],
            endidx-startidx+1,td.Fs),
            [x[k] for k in range(startidx,endidx+1)])
    def FirFilter(self):
        td=self.TimeDescriptor()
        return FirFilter(FilterDescriptor(1,-td.H*td.Fs,td.N-1),self.Values())