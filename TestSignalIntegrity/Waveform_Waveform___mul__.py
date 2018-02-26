class Waveform(list):
    def __mul__(self,other):
        if isinstance(other,WaveformProcessor):
            return other.ProcessWaveform(self)
        elif isinstance(other,(float,int,complex)):
            return Waveform(self.td,[v*other.real for v in self])
...
