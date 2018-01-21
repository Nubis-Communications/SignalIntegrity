class WaveformTrimmer(FilterDescriptor):
    def __init__(self,TrimLeft,TrimRight):
        FilterDescriptor.__init__(self,1,TrimRight,TrimLeft+TrimRight)
    def TrimWaveform(self,wf):
        K=wf.TimeDescriptor().K
        TL=self.TrimLeft()
        TT=self.TrimTotal()
        return Waveform(wf.TimeDescriptor()*self,
            [wf[k+TL] if 0 <= k+TL < K else 0. for k in range(K-TT)])