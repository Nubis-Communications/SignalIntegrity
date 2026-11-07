class WaveformDecimator(FilterDescriptor,WaveformProcessor):
    def __init__(self,decimationFactor,decimationPhase=0):
        self.df=decimationFactor
        self.dph=decimationPhase
        FilterDescriptor.__init__(self,1./decimationFactor,0,decimationPhase)
    def ProcessWaveform(self, wf):
        return self.DecimateWaveform(wf)
    def DecimateWaveform(self,wf):
        td=wf.td*self
        return Waveform(td,[wf[k*self.df+self.dph] for k in range(td.K)])
