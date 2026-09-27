class WaveformTrimmer(FilterDescriptor,WaveformProcessor):
    def __init__(self,TrimLeft,TrimRight):
        FilterDescriptor.__init__(self,1,TrimRight,TrimLeft+TrimRight)
    def ProcessWaveform(self, wf):
        return self.TrimWaveform(wf)
    def TrimWaveform(self,wf):
        K=wf.td.K
        TL=self.TrimLeft()
        TT=self.TrimTotal()
        return Waveform(wf.td*self,
            [wf[k+TL] if 0 <= k+TL < K else 0. for k in range(K-TT)])