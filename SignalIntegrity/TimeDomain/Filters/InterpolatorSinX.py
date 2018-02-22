'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
from FirFilter import FirFilter

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
        The filter is hard-coded to have 64 samples on each side of a center sample.
        In other words, it is 2*64+1=129 samples in length.
        """
        # pragma: silent exclude
        from FilterDescriptor import FilterDescriptor
        # pragma: include
        S=64
        U=1
        FirFilter.__init__(self,
            FilterDescriptor(U,S+F if accountForDelay else S,2*S),SinX(S,U,F))

class InterpolatorSinX(FirFilter):
    """sinx/x interpolating filter"""
    def __init__(self,U):
        """Constructor

        applies a sinx/x interpolating filter.

        @param U integer upsample factor of the filter.
        """
        # pragma: silent exclude
        from FilterDescriptor import FilterDescriptor
        # pragma: include
        S=64
        F=0.
        FirFilter.__init__(self,FilterDescriptor(U,S+F,2*S),SinX(S,U,F))
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
        from SignalIntegrity.TimeDomain.Waveform.Waveform import Waveform
        # pragma: include
        fd=self.FilterDescriptor()
        us=[0. for k in range(len(wf)*fd.U)]
        for k in range(len(wf)):
            us[k*fd.U]=wf.Values()[k]
        return FirFilter.FilterWaveform(self,Waveform(wf.td,us))

class InterpolatorFractionalDelayFilterSinX(object):
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
    def FilterWaveform(self,wf):
        """overloads base class FilterWaveform
        @param instance of class Waveform of waveform to process
        @return instance of class Waveform of wf upsampled and fractionally delayed
        """
        return self.usf.FilterWaveform(self.fdf.FilterWaveform(wf))