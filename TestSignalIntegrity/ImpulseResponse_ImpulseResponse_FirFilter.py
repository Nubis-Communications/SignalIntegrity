class ImpulseResponse(Waveform):
...
    def FirFilter(self):
        K=len(self)
        td=self.TimeDescriptor()
        return FirFilter(FilterDescriptor(1,-td.H*td.Fs,K-1),self.Values())