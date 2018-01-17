'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
from FilterDescriptor import FilterDescriptor

class WaveformTrimmer(FilterDescriptor):
    def __init__(self,TrimLeft,TrimRight):
        FilterDescriptor.__init__(self,1,TrimRight,TrimLeft+TrimRight)
    def TrimWaveform(self,wf):
        # pragma: silent exclude
        from SignalIntegrity.TimeDomain.Waveform.Waveform import Waveform
        # pragma: include
        K=wf.TimeDescriptor().N
        TL=self.TrimLeft()
        TT=self.TrimTotal()
        return Waveform(wf.TimeDescriptor()*self,
            [wf[k+TL] if 0 <= k+TL < K else 0. for k in range(K-TT)])