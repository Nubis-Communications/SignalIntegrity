class Waveform(list):
    def __mul__(self,other):
        if isinstance(other,WaveformProcessor):
            return other.ProcessWaveform(self)
        elif isinstance(other,(float,int,complex)):
            return Waveform(self.td,[v*other.real for v in self])
        elif isinstance(other,Waveform):
            [s,o]=AdaptedWaveforms([self,other])
            return Waveform(s.td,[s[k]*o[k] for k in range(len(s))])
...
