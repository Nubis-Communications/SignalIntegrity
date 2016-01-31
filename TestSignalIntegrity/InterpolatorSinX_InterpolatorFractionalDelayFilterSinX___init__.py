class InterpolatorFractionalDelayFilterSinX(object):
    def __init__(self,U,F,accountForDelay=True):
        self.fdf = FractionalDelayFilterSinX(F,accountForDelay)
        self.usf = InterpolatorSinX(U)
    def FilterWaveform(self,wf):
        return self.usf.FilterWaveform(self.fdf.FilterWaveform(wf))