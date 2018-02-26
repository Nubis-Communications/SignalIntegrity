# Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
# Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
# All Rights Reserved.
# 
# Explicit license in accompanying README.txt file.  If you don't have that file
# or do not agree to the terms in that file, then you are not licensed to use
# this material whatsoever.

from SignalIntegrity.TimeDomain.Filters.WaveformProcessor import WaveformProcessor
from SignalIntegrity.TimeDomain.Filters.FilterDescriptor import FilterDescriptor

class WaveformTrimmer(FilterDescriptor,WaveformProcessor):
    """trims waveforms"""
    def __init__(self,TrimLeft,TrimRight):
        """Constructor
        @param TrimLeft integer number of points to trim from left of waveform
        @param TrimRight integer number of points to trim from the right of waveform
        """
        FilterDescriptor.__init__(self,1,TrimRight,TrimLeft+TrimRight)
    def ProcessWaveform(self, wf):
        """process waveform

        Waveform trimmers process waveforms by trimming or padding them.

        @param wf instance of class Waveform to filter
        @return instance of class Waveform containing trimmed waveform
        @see TrimWaveform
        """
        return self.TrimWaveform(wf)
    def TrimWaveform(self,wf):
        """trim a waveform
        @param wf instance of class Waveform of waveform to trim
        @return instance of class Waveform containing trimmed waveform
        """
        # pragma: silent exclude
        from SignalIntegrity.TimeDomain.Waveform.Waveform import Waveform
        # pragma: include
        K=wf.td.K
        TL=self.TrimLeft()
        TT=self.TrimTotal()
        return Waveform(wf.td*self,
            [wf[k+TL] if 0 <= k+TL < K else 0. for k in range(K-TT)])