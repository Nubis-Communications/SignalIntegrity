from FilterDescriptor import FilterDescriptor

class WaveformTrimmer(FilterDescriptor):
    def __init__(self,TrimLeft,TrimRight):
        FilterDescriptor.__init__(self,1,TrimRight,TrimLeft+TrimRight)
    def TrimWaveform(self,wf):
        from SignalIntegrity.Waveform.Waveform import Waveform
        from SignalIntegrity.Waveform.TimeDescriptor import TimeDescriptor
        return Waveform(wf.TimeDescriptor()*self,
            [wf[k+self.TrimLeft()]
            for k in range(wf.TimeDescriptor().N-self.TrimTotal())])