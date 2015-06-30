from FirFilter import FirFilter

class FractionalDelayFilterLinear(FirFilter):
    def __init__(self,F,accountForDelay=True):
        from FilterDescriptor import FilterDescriptor
        FirFilter.__init__(self,FilterDescriptor(1,
            F if accountForDelay else 0,1),[1-F,F])

class UpsamplerLinear(FirFilter):
    def __init__(self,U):
        from FilterDescriptor import FilterDescriptor
        FirFilter.__init__(self,
            FilterDescriptor(U,(U-1.)/float(U),2*(U-1.)/float(U)),
            [float(u+1)/float(U) for u in range(U)]+
            [1-float(u+1)/float(U) for u in range(U-1)])
    def FilterWaveform(self,wf):
        from SignalIntegrity.TimeDomain.Waveform.Waveform import Waveform
        fd=self.FilterDescriptor()
        us=[0. for k in range(len(wf)*fd.U)]
        for k in range(len(wf)):
            us[k*fd.U]=wf.Values()[k]
        return FirFilter.FilterWaveform(self,Waveform(wf.TimeDescriptor(),us))

class UpsamplerFractionalDelayFilterLinear(object):
    def __init__(self,U,F,accountForDelay=True):
        self.fdf = FractionalDelayFilterLinear(F,accountForDelay)
        self.usf = UpsamplerLinear(U)
    def FilterWaveform(self,wf):
        return self.usf.FilterWaveform(self.fdf.FilterWaveform(wf))