class Waveform(object):
    def __mul__(self,other):
        if isinstance(other,FirFilter):
            return other.FilterWaveform(self)
        elif isinstance(other,WaveformTrimmer):
            return other.TrimWaveform(self)
        elif isinstance(other,WaveformDecimator):
            return other.DecimateWaveform(self)
        elif isinstance(other,float):
            return Waveform(self.m_t,[v*other for v in self.Values()])
...
