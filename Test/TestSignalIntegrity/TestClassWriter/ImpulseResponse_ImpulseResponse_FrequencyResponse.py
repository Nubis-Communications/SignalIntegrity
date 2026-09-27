class ImpulseResponse(Waveform):
...
    def FrequencyResponse(self,fd=None,adjustLength=True):
        if not fd and not adjustLength:
            X=fft.fft(self.Values())
            fd=self.td.FrequencyList()
            return FrequencyResponse(fd,[X[n] for n in range(fd.N+1)]).\
                _DelayBy(self.td.H)
        if not fd and adjustLength:
            return self._AdjustLength().FrequencyResponse(None,adjustLength=False)
        if fd:
            return self.FrequencyResponse().Resample(fd)
    def _AdjustLength(self):
        td = self.td
        PositivePoints = int(max(0,math.floor(td.H*td.Fs+td.K+0.5)))
        NegativePoints = int(max(0,math.floor(-td.H*td.Fs+0.5)))
        P=max(PositivePoints,NegativePoints)*2
        return self._Pad(P)
...
