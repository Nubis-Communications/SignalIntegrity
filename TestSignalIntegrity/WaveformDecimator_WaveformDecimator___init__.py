class WaveformDecimator(FilterDescriptor):
    def __init__(self,decimationFactor,decimationPhase=1):
        self.df=decimationFactor
        self.dph=decimationPhase
        FilterDescriptor.__init__(self,1./decimationFactor,0,decimationPhase)
    def DecimateWaveform(self,wf):
        td=wf.TimeDescriptor()*self
        return Waveform(td,[wf[k*self.df+self.dph] for k in range(td.N)])
