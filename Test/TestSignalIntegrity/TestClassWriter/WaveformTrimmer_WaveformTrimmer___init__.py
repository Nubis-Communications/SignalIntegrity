class WaveformTrimmer(FilterDescriptor,WaveformProcessor):
    def __init__(self,TrimLeft,TrimRight):
        FilterDescriptor.__init__(self,1,TrimRight,TrimLeft+TrimRight)
    def ProcessWaveform(self, wf):
        return self.TrimWaveform(wf)
    def TrimWaveform(self,wf):
        K=wf.td.K
        TL=self.TrimLeft()
        TT=self.TrimTotal()
        newtd=wf.td*self
        N=K-TT
        if N<=0:
            return Waveform(newtd,[])
        if TL>=0 and TL+N<=K:
            # no padding required (the common adaption case): a plain list slice
            # preserves the sample values exactly while avoiding a Python
            # per-sample loop over potentially very large waveforms.
            return Waveform(newtd,wf[TL:TL+N])
        return Waveform(newtd,
            [wf[k+TL] if 0 <= k+TL < K else 0. for k in range(N)])