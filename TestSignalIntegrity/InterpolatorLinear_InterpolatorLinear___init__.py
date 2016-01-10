class InterpolatorLinear(FirFilter):
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

