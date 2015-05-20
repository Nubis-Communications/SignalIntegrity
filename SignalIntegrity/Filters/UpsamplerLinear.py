from FirFilter import FirFilter
import copy

class UpsamplerLinear(FirFilter):
    def __init__(self,U,F,accountForDelay=True):
        from FilterDescriptor import FilterDescriptor
        L=2.
        ft0=[float(u+1)/float(U)-F/U for u in range(U)]
        ft1=[1-ft0[u] for u in range(U)]
        ft=ft0+ft1
        if not accountForDelay: F=0.
        #fd = FilterDescriptor(1,F,1)*FilterDescriptor(U,0.,0.)
        fd = FilterDescriptor(U,(F+U-1)/float(U),1)
        FirFilter.__init__(self,fd,ft)
    def FilterWaveform(self,wf):
        from SignalIntegrity.Waveform.Waveform import Waveform
        from SignalIntegrity.Waveform.TimeDescriptor import TimeDescriptor
        fd=self.FilterDescriptor()
        us=[0. for k in range(len(wf)*fd.U+fd.U-1)]
        for k in range(len(wf)):
            us[k*fd.U+fd.U-1]=wf.Values()[k]
        return FirFilter.FilterWaveform(self,Waveform(wf.TimeDescriptor(),us))