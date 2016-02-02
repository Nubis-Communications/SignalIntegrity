'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
from FirFilter import FirFilter

import math

def SinXFunc(k,S,U,F):
    if float(k)/U-F-S==0:
        return 1.
    else:
        return math.sin(math.pi*(float(k)/U-F-S))/(math.pi*(float(k)/U-F-S))*\
            (1./2.+1./2.*math.cos(math.pi*(float(k)/U-S)/S))

class FractionalDelayFilterSinX(FirFilter):
    def __init__(self,F,accountForDelay=True):
        # pragma: silent exclude
        from FilterDescriptor import FilterDescriptor
        # pragma: include
        S=64
        U=1
        FirFilter.__init__(self,
            FilterDescriptor(U,S+F if accountForDelay else S,2*S),
            [SinXFunc(k,S,U,F) for k in range(2*U*S+1)])

class InterpolatorSinX(FirFilter):
    def __init__(self,U):
        # pragma: silent exclude
        from FilterDescriptor import FilterDescriptor
        # pragma: include
        S=64
        F=0.
        FirFilter.__init__(self,
            FilterDescriptor(U,S+F,2*S),
            [SinXFunc(k,S,U,F) for k in range(2*U*S+1)])
    def FilterWaveform(self,wf):
        # pragma: silent exclude
        from SignalIntegrity.TimeDomain.Waveform.Waveform import Waveform
        # pragma: include
        fd=self.FilterDescriptor()
        us=[0. for k in range(len(wf)*fd.U)]
        for k in range(len(wf)):
            us[k*fd.U]=wf.Values()[k]
        return FirFilter.FilterWaveform(self,Waveform(wf.TimeDescriptor(),us))

class InterpolatorFractionalDelayFilterSinX(object):
    def __init__(self,U,F,accountForDelay=True):
        self.fdf = FractionalDelayFilterSinX(F,accountForDelay)
        self.usf = InterpolatorSinX(U)
    def FilterWaveform(self,wf):
        return self.usf.FilterWaveform(self.fdf.FilterWaveform(wf))