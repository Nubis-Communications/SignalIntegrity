class InterpolatorFractionalDelayFilterLinear(object):
    def __init__(self,U,F,accountForDelay=True):
        self.fdf = FractionalDelayFilterLinear(F,accountForDelay)
        self.usf = InterpolatorLinear(U)
    def FilterWaveform(self,wf):
        return self.usf.FilterWaveform(self.fdf.FilterWaveform(wf))