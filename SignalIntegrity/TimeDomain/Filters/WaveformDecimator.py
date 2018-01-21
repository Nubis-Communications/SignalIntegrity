'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
from FilterDescriptor import FilterDescriptor

class WaveformDecimator(FilterDescriptor):
    def __init__(self,decimationFactor,decimationPhase=1):
        self.df=decimationFactor
        self.dph=decimationPhase
        FilterDescriptor.__init__(self,1./decimationFactor,0,decimationPhase)
    def DecimateWaveform(self,wf):
        # pragma: silent exclude
        from SignalIntegrity.TimeDomain.Waveform.Waveform import Waveform
        # pragma: include       
        td=wf.td*self
        return Waveform(td,[wf[k*self.df+self.dph] for k in range(td.K)])
