"""
InterpolatorLinear.py
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

from SignalIntegrity.Lib.TimeDomain.Filters.FirFilter import FirFilter
from SignalIntegrity.Lib.TimeDomain.Filters.WaveformProcessor import WaveformProcessor

class FractionalDelayFilterLinear(FirFilter):
    """linear fractional delay filter"""
    def __init__(self,F,accountForDelay=True):
        """Constructor

        applies a two-tap linear interpolating filter.

        @param F float amount of delay to apply.  The delay is in samples of the input waveform.
        @param accountForDelay (optional) boolean whether to account for the delay
        @remark
        if accountForDelay, then the filter provides a sample phase adjustment, meaning
        that there is no actual delay applied to the waveform, but the time axis under
        the waveform is shifted.  This is the usual way to apply this filter and is used
        to adapt waveforms on different time axes to each other.\n
        if not accountForDelay, then the filter actually delays waveforms by the delay
        specified.
        """
        # pragma: silent exclude
        from SignalIntegrity.Lib.TimeDomain.Filters.FilterDescriptor import FilterDescriptor
        # pragma: include
        FirFilter.__init__(self,FilterDescriptor(1,
            (F if F >= 0 else 1+F) if accountForDelay else 0,1),
            [1-F,F] if F >= 0 else [-F,1+F])

class InterpolatorLinear(FirFilter):
    """linear interpolating filter"""
    def __init__(self,U):
        """Constructor

        applies a linear interpolating filter.

        @param U integer upsample factor of the filter.
        """
        # pragma: silent exclude
        from SignalIntegrity.Lib.TimeDomain.Filters.FilterDescriptor import FilterDescriptor
        # pragma: include
        FirFilter.__init__(self,
            FilterDescriptor(U,(U-1.)/float(U),2*(U-1.)/float(U)),
            [float(u+1)/float(U) for u in range(U)]+
            [1-float(u+1)/float(U) for u in range(U-1)])
    def FilterWaveform(self,wf):
        """overloads base class FilterWaveform
        @param wf instance of class Waveform
        @return instance of class Waveform containing the upsampled, interpolated wf
        @remark
        This method first classically upsamples the waveform by inserting zeros
        between the samples and then passes the upsampled waveform through the linear
        interpolation filter.
        """
        # pragma: silent exclude
        from SignalIntegrity.Lib.TimeDomain.Waveform.Waveform import Waveform
        # pragma: include
        fd=self.FilterDescriptor()
        us=[0. for k in range(len(wf)*fd.U)]
        for k in range(len(wf)):
            us[k*fd.U]=wf[k]
        return FirFilter.FilterWaveform(self,Waveform(wf.td,us))

class InterpolatorFractionalDelayFilterLinear(WaveformProcessor):
    """combination linear fractional delay and interpolating filter"""
    def __init__(self,U,F,accountForDelay=True):
        """Constructor
        @param U integer upsample factor of the filter.
        @param F float amount of delay to apply.  The delay is in samples of the input waveform.
        @param accountForDelay (optional) boolean whether to account for the delay
        @remark
        if accountForDelay, then the filter provides a sample phase adjustment, meaning
        that there is no actual delay applied to the waveform, but the time axis under
        the waveform is shifted.  This is the usual way to apply this filter and is used
        to adapt waveforms on different time axes to each other.\n
        if not accountForDelay, then the filter actually delays waveforms by the delay
        specified.
        """
        self.fdf = FractionalDelayFilterLinear(F,accountForDelay)
        self.usf = InterpolatorLinear(U)
    def ProcessWaveform(self, wf):
        """process waveform

        waveforms are processed with both an interpolation and fractional delay filter.

        @param wf instance of class Waveform to filter
        @return instance of class Waveform of wf upsampled and fractionally delayed

        @see FilterWaveform
        """
        return self.FilterWaveform(wf)
    def FilterWaveform(self,wf):
        """overloads base class FilterWaveform
        @param wf instance of class Waveform of waveform to process
        @return instance of class Waveform of wf upsampled and fractionally delayed
        """
        return self.usf.FilterWaveform(self.fdf.FilterWaveform(wf))
