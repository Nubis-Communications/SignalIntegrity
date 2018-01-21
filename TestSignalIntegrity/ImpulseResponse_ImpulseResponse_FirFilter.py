class ImpulseResponse(Waveform):
...
    def FirFilter(self):
        td=self.td
        return FirFilter(FilterDescriptor(1,-td.H*td.Fs,td.K-1),self.Values())