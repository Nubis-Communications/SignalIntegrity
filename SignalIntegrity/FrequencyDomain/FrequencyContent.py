'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
import math
import cmath

from SignalIntegrity.FrequencyDomain.FrequencyDomain import FrequencyDomain
from SignalIntegrity.Splines import Spline

class FrequencyContent(FrequencyDomain):
    def __init__(self,f=None,resp=None):
        FrequencyDomain.__init__(self,f,resp)
    def Content(self,unit=None):
        return self.Values(unit)
    def _DelayBy(self,TD):
        fd=self.FrequencyList()
        return FrequencyContent(fd,
        [self.Content()[n]*cmath.exp(-1j*2.*math.pi*fd[n]*TD)
            for n in range(fd.N+1)])