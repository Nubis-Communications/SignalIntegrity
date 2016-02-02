'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
from FirFilter import FirFilter

class FractionalDelayFilterLinear(FirFilter):
    def __init__(self,F,accountForDelay=True):
        # pragma: silent exclude
        from FilterDescriptor import FilterDescriptor
        # pragma: include
        FirFilter.__init__(self,FilterDescriptor(1,
            F if accountForDelay else 0,1),[1-F,F])

class InterpolatorLinear(FirFilter):
    def __init__(self,U):
        # pragma: silent exclude
        from FilterDescriptor import FilterDescriptor
        # pragma: include
        FirFilter.__init__(self,
            FilterDescriptor(U,(U-1.)/float(U),2*(U-1.)/float(U)),
            [float(u+1)/float(U) for u in range(U)]+
            [1-float(u+1)/float(U) for u in range(U-1)])
    def FilterWaveform(self,wf):
        # pragma: silent exclude
        from SignalIntegrity.TimeDomain.Waveform.Waveform import Waveform
        # pragma: include
        fd=self.FilterDescriptor()
        us=[0. for k in range(len(wf)*fd.U)]
        for k in range(len(wf)):
            us[k*fd.U]=wf.Values()[k]
        return FirFilter.FilterWaveform(self,Waveform(wf.TimeDescriptor(),us))

class InterpolatorFractionalDelayFilterLinear(object):
    def __init__(self,U,F,accountForDelay=True):
        self.fdf = FractionalDelayFilterLinear(F,accountForDelay)
        self.usf = InterpolatorLinear(U)
    def FilterWaveform(self,wf):
        return self.usf.FilterWaveform(self.fdf.FilterWaveform(wf))