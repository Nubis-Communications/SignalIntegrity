class InterpolatorSinX(FirFilter):
    def __init__(self,U):
        from FilterDescriptor import FilterDescriptor
        S=64
        F=0.
        FirFilter.__init__(self,
            FilterDescriptor(U,S+F,2*S),
            [SinXFunc(k,S,U,F) for k in range(2*U*S+1)])
    def FilterWaveform(self,wf):
        from SignalIntegrity.TimeDomain.Waveform.Waveform import Waveform
        fd=self.FilterDescriptor()
        us=[0. for k in range(len(wf)*fd.U)]
        for k in range(len(wf)):
            us[k*fd.U]=wf.Values()[k]
        return FirFilter.FilterWaveform(self,Waveform(wf.TimeDescriptor(),us))

