class InterpolatorSinX(FirFilter):
    def __init__(self,U):
        F=0.
        FirFilter.__init__(self,FilterDescriptor(U,self.S+F,2*self.S),SinX(self.S,U,F))
    def FilterWaveform(self,wf):
        fd=self.FilterDescriptor()
        us=np.zeros(len(wf)*fd.U,dtype=wf.values.dtype)
        us[::fd.U]=wf.values
        return FirFilter.FilterWaveform(self,Waveform(wf.td,us))

