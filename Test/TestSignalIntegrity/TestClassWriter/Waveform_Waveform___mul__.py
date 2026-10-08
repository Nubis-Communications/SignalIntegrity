class Waveform(object):
    def __mul__(self,other):
        if isinstance(other,FrequencyResponse):
            return self * other.ImpulseResponse()
        elif isinstance(other,ImpulseResponse):
            return self * other.FirFilter()
        if isinstance(other,WaveformProcessor):
            return other.ProcessWaveform(self)
        elif isinstance(other,(float,int,complex)):
            result=copy(self)
            result.values=result.values*other.real
            return result
        elif isinstance(other,Waveform):
            [s,o]=AdaptedWaveforms([self,other])
            return Waveform(s.td,s.values*o.values)
...
