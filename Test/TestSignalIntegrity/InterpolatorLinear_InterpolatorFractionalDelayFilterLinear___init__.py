class InterpolatorFractionalDelayFilterLinear(WaveformProcessor):
    def __init__(self,U,F,accountForDelay=True):
        self.fdf = FractionalDelayFilterLinear(F,accountForDelay)
        self.usf = InterpolatorLinear(U)
    def ProcessWaveform(self, wf):
        return self.FilterWaveform(wf)
    def FilterWaveform(self,wf):
        return self.usf.FilterWaveform(self.fdf.FilterWaveform(wf))