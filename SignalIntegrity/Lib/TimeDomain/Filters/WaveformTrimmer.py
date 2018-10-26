"""
WaveformTrimmer.py
"""

# Copyright (c) 2018 Teledyne LeCroy, Inc.
# All rights reserved worldwide.
#
# This file is part of SignalIntegrity.
#
# SignalIntegrity is free software: You can redistribute it and/or modify it under the terms
# of the GNU General Public License as published by the Free Software Foundation, either
# version 3 of the License, or any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <https://www.gnu.org/licenses/>

from SignalIntegrity.Lib.TimeDomain.Filters.WaveformProcessor import WaveformProcessor
from SignalIntegrity.Lib.TimeDomain.Filters.FilterDescriptor import FilterDescriptor

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
        from SignalIntegrity.Lib.TimeDomain.Waveform.Waveform import Waveform
        # pragma: include
        K=wf.td.K
        TL=self.TrimLeft()
        TT=self.TrimTotal()
        return Waveform(wf.td*self,
            [wf[k+TL] if 0 <= k+TL < K else 0. for k in range(K-TT)])