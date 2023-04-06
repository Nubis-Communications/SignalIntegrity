class Waveform(list):
    def __mul__(self,other):
        if isinstance(other,WaveformProcessor):
            return other.ProcessWaveform(self)
        elif isinstance(other,(float,int,complex)):
            result=copy(self)
            for k in range(len(result)): result[k]*=other.real
            return result
        elif isinstance(other,Waveform):
            [s,o]=AdaptedWaveforms([self,other])
            return Waveform(s.td,[s[k]*o[k] for k in range(len(s))])
...
