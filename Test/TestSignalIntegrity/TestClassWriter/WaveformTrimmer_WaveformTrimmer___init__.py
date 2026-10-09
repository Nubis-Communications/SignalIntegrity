class WaveformTrimmer(FilterDescriptor,WaveformProcessor):
    def __init__(self,TrimLeft,TrimRight):
        FilterDescriptor.__init__(self,1,TrimRight,TrimLeft+TrimRight)
    def ProcessWaveform(self, wf):
        return self.TrimWaveform(wf)
    def TrimWaveform(self,wf):
        K=wf.td.K
        TL=self.TrimLeft()
        TT=self.TrimTotal()
        newtd=wf.td*self
        N=K-TT
        if N<=0:
            return Waveform(newtd,np.array([],dtype=wf.values.dtype))
        # map output sample k to input sample k+TL, zero-filling where out of range
        out=np.zeros(N,dtype=wf.values.dtype)
        idx=np.arange(N)+TL
        valid=(idx>=0)&(idx<K)
        out[valid]=wf.values[idx[valid]]
        return Waveform(newtd,out)
