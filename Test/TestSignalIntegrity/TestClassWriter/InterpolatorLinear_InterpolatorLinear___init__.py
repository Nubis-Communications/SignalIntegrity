class InterpolatorLinear(FirFilter):
    def __init__(self,U):
        FirFilter.__init__(self,
            FilterDescriptor(U,(U-1.)/float(U),2*(U-1.)/float(U)),
            np.concatenate((np.arange(1,U+1)/float(U),
                            1.-np.arange(1,U)/float(U))))
    def FilterWaveform(self,wf):
        fd=self.FilterDescriptor()
        us=np.zeros(len(wf)*fd.U,dtype=wf.values.dtype)
        us[::fd.U]=wf.values
        return FirFilter.FilterWaveform(self,Waveform(wf.td,us))

