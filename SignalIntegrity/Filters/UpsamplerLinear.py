from FirFilter import FirFilter
import copy

class FractionalDelayFilter(FirFilter):
    def __init__(self,F,accountForDelay=True):
        from FilterDescriptor import FilterDescriptor
        FirFilter.__init__(self,FilterDescriptor(1,F if accountForDelay else 0,1),[1-F,F])

class Upsampler(FirFilter):
    def __init__(self,U):
        from FilterDescriptor import FilterDescriptor
        FirFilter.__init__(self,
            FilterDescriptor(U,(U-1.)/float(U),1),
            [float(u+1)/float(U) for u in range(U)]+
            [1-float(u+1)/float(U) for u in range(U)])
    def FilterWaveform(self,wf):
        from SignalIntegrity.Waveform.Waveform import Waveform
        from SignalIntegrity.Waveform.TimeDescriptor import TimeDescriptor
        fd=self.FilterDescriptor()
        us=[0. for k in range(len(wf)*fd.U+fd.U-1)]
        for k in range(len(wf)):
            us[k*fd.U+fd.U-1]=wf.Values()[k]
        return FirFilter.FilterWaveform(self,Waveform(wf.TimeDescriptor(),us))

class UpsamplerLinear(object):
    def __init__(self,U,F,accountForDelay=True):
        self.fdf = FractionalDelayFilter(F,accountForDelay)
        self.usf = Upsampler(U)
    def FilterWaveform(self,wf):
        return self.usf.FilterWaveform(self.fdf.FilterWaveform(wf))