"""
FirFilter.py
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

from numpy import convolve
#from PySICppLib import PySIConvolve

class FirFilter(WaveformProcessor):
    """base filter class for all FIR filters"""
    def __init__(self,fd,ft):
        """Constructor
        @param fd instance of class FilterDescriptor describing the time axis effects
        of this filter.
        @param ft list of float filter taps
        """
        self.m_fd = fd
        self.m_ft=ft
    def ProcessWaveform(self, wf):
        """process waveform

        FIR filters process waveforms by filtering them.

        @param wf instance of class Waveform to filter
        @return instance of class Waveform containing this filter applied to wf
        @see FilterWaveform
        """
        return self.FilterWaveform(wf)
    def FilterTaps(self):
        """return the filter taps
        @return list of float filter taps
        """
        return self.m_ft
    def FilterDescriptor(self):
        """returns the filter descriptor
        @return instance of class FilterDescriptor
        """
        return self.m_fd
    def FilterWaveform(self,wf):
        """filters a waveform
        @param wf instance of class Waveform
        @return instance of class Waveform containing this filter applied to wf
        """
        # pragma: silent exclude
        from SignalIntegrity.Lib.TimeDomain.Waveform.Waveform import Waveform
        # pragma: include
        td = wf.td*self.FilterDescriptor()
        # pragma: silent exclude
        #filteredwf=PySIConvolve(wf.Values(),self.FilterTaps())
        # pragma: include
        filteredwf=convolve(wf.Values(),self.FilterTaps(),'valid').tolist()
        return Waveform(td,filteredwf)
    def Print(self):
        """prints an ASCII description of the filter"""
        self.FilterDescriptor().Print()
        print(str(self.FilterTaps()))
