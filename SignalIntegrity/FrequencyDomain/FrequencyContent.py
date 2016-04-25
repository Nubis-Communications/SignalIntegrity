'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
from numpy import fft
import math
import cmath

from SignalIntegrity.FrequencyDomain.FrequencyDomain import FrequencyDomain
from SignalIntegrity.FrequencyDomain.FrequencyList import FrequencyList
from SignalIntegrity.FrequencyDomain.FrequencyList import EvenlySpacedFrequencyList
from SignalIntegrity.TimeDomain.Waveform.ImpulseResponse import ImpulseResponse
from SignalIntegrity.TimeDomain.Waveform.TimeDescriptor import TimeDescriptor
from SignalIntegrity.Splines import Spline
from SignalIntegrity.ChirpZTransform import CZT

class FrequencyContent(FrequencyDomain):
    def __init__(self,f=None,resp=None):
        FrequencyDomain.__init__(self,f,resp)
    def _DelayBy(self,TD):
        fd=self.FrequencyList()
        return FrequencyContent(fd,
        [self.Response()[n]*cmath.exp(-1j*2.*math.pi*fd[n]*TD)
            for n in range(fd.N+1)])
    def _SplineResample(self,fdp):
        fd=self.FrequencyList()
        Poly=Spline(fd,self.Response())
        newresp=[Poly.Evaluate(f) if f <= fd[-1] else 0.0001 for f in fdp]
        return FrequencyContent(fdp,newresp)
