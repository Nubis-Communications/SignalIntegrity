"""
InterpolatorSinX.py
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

import math

def SinX(S,U,F):
    """calculates the sinX/X filter taps for Sinx filters
    @param S integer side samples for filter (without upsampling)
    @param U integer upsample factor
    @param F float fractional delay
    @remark
    The filter is 2*S*U+1 in length, meaning it has S*U samples on each side of a center
    sample point.
    """
    sl=[1. if float(k)/U-F-S==0 else
        math.sin(math.pi*(float(k)/U-F-S))/(math.pi*(float(k)/U-F-S))*\
        (1./2.+1./2.*math.cos(math.pi*(float(k)/U-S)/S))
        for k in range(2*U*S+1)]
    s=sum(sl)/U
    sl=[sle/s for sle in sl]
    return sl

class FractionalDelayFilterSinX(FirFilter):
    """sinx/x fractional delay filter"""
    S=64
    def __init__(self,F,accountForDelay=True):
        """Constructor

        applies sinx/x interpolating filter.

        @param F float amount of delay to apply.  The delay is in samples of the input waveform.
        @param accountForDelay (optional) boolean whether to account for the delay
        @remark
        if accountForDelay, then the filter provides a sample phase adjustment, meaning
        that there is no actual delay applied to the waveform, but the time axis under
        the waveform is shifted.  This is the usual way to apply this filter and is used
        to adapt waveforms on different time axes to each other.\n
        if not accountForDelay, then the filter actually delays waveforms by the delay
        specified.
        @remark
        The filter is hard-coded  in a static member to have 64 samples on each side of a center sample.
        In other words, it is 2*64+1=129 samples in length.
        """
        # pragma: silent exclude
        from SignalIntegrity.Lib.TimeDomain.Filters.FilterDescriptor import FilterDescriptor
        # pragma: include
        U=1
        FirFilter.__init__(self,
            FilterDescriptor(U,self.S+F if accountForDelay else self.S,2*self.S),
                SinX(self.S,U,F))

class InterpolatorSinX(FirFilter):
    """sinx/x interpolating filter"""
    S=64
    def __init__(self,U):
        """Constructor

        applies a sinx/x interpolating filter.

        @param U integer upsample factor of the filter.
        """
        # pragma: silent exclude
        from SignalIntegrity.Lib.TimeDomain.Filters.FilterDescriptor import FilterDescriptor
        # pragma: include
        F=0.
        FirFilter.__init__(self,FilterDescriptor(U,self.S+F,2*self.S),SinX(self.S,U,F))
    def FilterWaveform(self,wf):
        """overloads base class FilterWaveform
        @param wf instance of class Waveform
        @return instance of class Waveform containing the upsampled, interpolated wf
        @remark
        This method first classically upsamples the waveform by inserting zeros
        between the samples and then passes the upsampled waveform through the sinx/x
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

class InterpolatorFractionalDelayFilterSinX(WaveformProcessor):
    """combination sinx/x fractional delay and interpolating filter"""
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
        self.fdf = FractionalDelayFilterSinX(F,accountForDelay)
        self.usf = InterpolatorSinX(U)
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