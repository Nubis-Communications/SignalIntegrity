from FirFilter import FirFilter

import copy
import math

def SinXFunc(ku,K,U,F):
    if float(ku)/U-F-K/2==0:
        return 1.
    else:
        return math.sin(math.pi*(float(ku)/U-F-K/2))/(math.pi*(float(ku)/U-F-K/2))*\
            (1./2.+1./2.*math.cos(math.pi*(float(ku)/U-K/2)/(K/2)))

class FractionalDelayFilterSinX(FirFilter):
    def __init__(self,F,accountForDelay=True):
        from FilterDescriptor import FilterDescriptor
        K=128
        U=1
        FirFilter.__init__(self,
            FilterDescriptor(U,K/2+F if accountForDelay else K/2,K-1),
            [SinXFunc(ku,K,U,F) for ku in range(K)])

class UpsamplerSinX(FirFilter):
    def __init__(self,U):
        from FilterDescriptor import FilterDescriptor
        K=128
        F=0.
        FirFilter.__init__(self,
            FilterDescriptor(U,K/2,K-1),
            [SinXFunc(ku,K,U,F) for ku in range(K*U)])
    def FilterWaveform(self,wf):
        from SignalIntegrity.TimeDomain.Waveform.Waveform import Waveform
        from SignalIntegrity.TimeDomain.Waveform.TimeDescriptor import TimeDescriptor
        fd=self.FilterDescriptor()
        us=[0. for k in range(len(wf)*fd.U+fd.U-1)]
        for k in range(len(wf)):
            us[k*fd.U+fd.U-1]=wf.Values()[k]
        return FirFilter.FilterWaveform(self,Waveform(wf.TimeDescriptor(),us))

class UpsamplerFractionalDelayFilterSinX(object):
    def __init__(self,U,F,accountForDelay=True):
        self.fdf = FractionalDelayFilterSinX(F,accountForDelay)
        self.usf = UpsamplerSinX(U)
    def FilterWaveform(self,wf):
        return self.usf.FilterWaveform(self.fdf.FilterWaveform(wf))