"""
WaveformDecimator.py
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

class WaveformDecimator(FilterDescriptor,WaveformProcessor):
    """decimates waveforms"""
    def __init__(self,decimationFactor,decimationPhase=0):
        """Constructor
        @param decimationFactor integer decimation factor
        @param decimationPhase integer decimation phase.  This is the index of the first sample
        retained from the waveform to be decimated.
        """
        self.df=decimationFactor
        self.dph=decimationPhase
        FilterDescriptor.__init__(self,1./decimationFactor,0,decimationPhase)
    def ProcessWaveform(self, wf):
        """process waveform

        Waveform decimators process waveforms by decimating them.

        @param wf instance of class Waveform to filter
        @return intance of class Waveform the decimated waveform
        @see DecimateWaveform
        """
        return self.DecimateWaveform(wf)
    def DecimateWaveform(self,wf):
        """decimates a waveform
        @param wf instance of class Waveform of waveform to be decimated
        @return intance of class Waveform the decimated waveform
        """
        # pragma: silent exclude
        from SignalIntegrity.Lib.TimeDomain.Waveform.Waveform import Waveform
        # pragma: include       
        td=wf.td*self
        return Waveform(td,[wf[k*self.df+self.dph] for k in range(td.K)])
