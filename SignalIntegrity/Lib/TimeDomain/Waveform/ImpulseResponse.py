"""
ImpulseResponse.py
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

from numpy import fft
import math

from SignalIntegrity.Lib.TimeDomain.Waveform.TimeDescriptor import TimeDescriptor
from SignalIntegrity.Lib.TimeDomain.Waveform.Waveform import Waveform
from SignalIntegrity.Lib.TimeDomain.Filters.FilterDescriptor import FilterDescriptor
from SignalIntegrity.Lib.TimeDomain.Filters.FirFilter import FirFilter

class ImpulseResponse(Waveform):
    """impulse response of a filter as a waveform"""
    def __init__(self,t=None,td=None):
        """constructor
        @param t instance of class TimeDescriptor describing time-axis of impulse response
        @param td list of float representing time-domain values
        @remark note that t can be an instance of waveform and td None which causes the impulse response
        to be instantiated dircectly from a waveform.
        """
        if isinstance(t,Waveform):
            Waveform.__init__(self,t.td,t)
        else:
            Waveform.__init__(self,t,td)
    def DelayBy(self,d):
        """delays the impulse response

        delays the impulse response by modifying the time-axis under the response.

        @param d float time to delay the response by.
        """
        return ImpulseResponse(self.td.DelayBy(d),self.Values())
    def FrequencyResponse(self,fd=None,adjustLength=True):
        """produces the frequency response

        impulse responses and frequency responses are equivalent and can be converted back
        and forth into each other.  This method converts the impulse response to its corresponding
        frequency domain equivalent.

        @attention users of this function should only either supply the fd argument or not.  Not
        supplying the argument provides the generic frequency response associated with this impulse
        response such that self.FrequencyResponse().ImpulseResponse() provides the same answer.

        Supplying fd supplies the resulting frequency response resampled onto another frequency scale.

        @param fd (optional) instance of class FrequencyList (defaults to None).
        @param adjustLength (optional) bool whether to adjust the length. (defaults to True).

        @note All impulse responses are evenly spaced

        @note whether a frequency descriptor is specified and whether to adjust length determines
        all possibilities of what can happen:

        | fd        | adjustLength | Generates:                              |
        |:---------:|:------------:|:---------------------------------------:|
        | None      |   False      | generic frequency response              |
        | None      |   True       | frequency response with length adjusted |
        | provided  |   don't care | CZT resamples to fd (adjusts length)    |

        The frequency descriptor, if provided, provides the frequency points to resample to, otherwise
        the frequency descriptor associated with the internal time descriptor inherent to the impulse
        response is used.

        Length adjustment means that although the impulse response may start at time zero, or some
        other time, the assumption is that there are an equal number of points for negative and positve
        time and that time zero is in the center of these points.

        This assumption for length adjustment is what allows an impulse response to be filled in with
        positive only times, but allow an equality to exist between all frequency responses and impulse
        responses.

        Basically, the time adjustment can be seen as calculating the number of points before time zero
        and the number of points after time zero and calculating the total number of points in the waveform
        (for the purposes of frequency response calculation) as the max of these two numbers multiplied by two.
        """
        # pragma: silent exclude
        from SignalIntegrity.Lib.FrequencyDomain.FrequencyResponse import FrequencyResponse
        # pragma: include
        if not fd and not adjustLength:
            X=fft.fft(self.Values())
            fd=self.td.FrequencyList()
            return FrequencyResponse(fd,[X[n] for n in range(fd.N+1)]).\
                _DelayBy(self.td.H)
        if not fd and adjustLength:
            return self._AdjustLength().FrequencyResponse(None,adjustLength=False)
        if fd:
            return self.FrequencyResponse().Resample(fd)
    def _AdjustLength(self):
        """adjusts the length of the impulse response

        Calculates the number of points in the impulse response as twice the maximimum of the positive and
        negative time-domain points.

        @return instance of class ImpulseResponse with the impulse centered at time zero, an even number of
        points, and an equal number of points before and after time zero.
        """
        td = self.td
        PositivePoints = int(max(0,math.floor(td.H*td.Fs+td.K+0.5)))
        NegativePoints = int(max(0,math.floor(-td.H*td.Fs+0.5)))
        P=max(PositivePoints,NegativePoints)*2
        return self._Pad(P)
    def _Pad(self,P):
        """Pads the impulse response

        The impulse response is padded to P points with an equal number of points before and after
        time zero.

        @param P integer number of points to pad the impulse response to.
        @return an instance of class ImpulseResponse with the zero padded points.
        @attention P must be even - not checked - it must add equal points to the left
            and right of the impulse response.
        @note
        if K is the number of points in the selfs frequency response then:

        | P and K  | outcome
        |:--------:|:--------------------------------------------:|
        | P==K     | the original response is returned            |
        | P<K      | the response is truncated to P time points   |
        | P>K      | the response is zero padded to P time points |
        """
        K=len(self)
        if P==K: x = self.Values()
        elif P<K: x=[self[k] for k in range((K-P)//2,K-(K-P)//2)]
        else:
            x=[0 for p in range((P-K)//2)]
            x=x+self.Values()+x
        td = self.td
        return ImpulseResponse(TimeDescriptor(td.H-(P-K)/2./td.Fs,P,td.Fs),x)
    def _FractionalDelayTime(self):
        """fractional delay time of impulse response

        returns the fraction of the sample time since time zero containing the first positive point in the
        impulse response.

        @return fractional number of samples of delay.

        @note this can be a positive or negative number and will be the between -0.5 and 0.5
        """
        td=self.td
        TD=-(-td.H*td.Fs-math.floor(-td.H*td.Fs+0.5))/td.Fs
        return TD
    def Resample(self,td):
        """resamples the impulse response to a specified time descriptor
        @param td instance of class TimeDescriptor containing new time descriptor.
        @return an instance of class ImpulseResponse containing impulse response with new
        time descriptor.
        """
        fr=self.FrequencyResponse()
        return fr.ImpulseResponse(td)
    def TrimToThreshold(self,threshold):
        """truncates an impulse response, keeping only the values above or equal to specified threshold.

        This is useful for reducing computational complexity in processing.

        @param threshold float threshold to apply to the values in the waveform.
        @attention the threshold specified is a fraction of the maximum absolute value of the values
        in the waveform.
        @note that absolute values are utilized in value/threshold comparison.
        @note the trimming is performed by finding the lowest and highest time value above or equal
        to the threshold - all values between these times are retained.
        """
        x=self.Values()
        td=self.td
        maxabsx=max(self.Values('abs'))
        minv=maxabsx*threshold
        for k in range(len(x)):
            if abs(x[k]) >= minv:
                startidx = k
                break
        for k in range(len(x)):
            ki = len(x)-1-k
            if abs(x[ki]) >= minv:
                endidx = ki
                break
        if (endidx-startidx+1)//2*2 != endidx-startidx+1:
            # the result would not have an even number of points
            if endidx < len(x)-1:
                # keep a point at the end if possible
                endidx = endidx + 1
            elif startidx > 0:
                # keep a point at the beginning if possible
                startidx = startidx - 1
            else:
                # append a zero to the end and calculate number of
                # points with endidx+1
                return ImpulseResponse(TimeDescriptor(td[startidx],
                    (endidx+1)-startidx+1,td.Fs),
                    [x[k] for k in range(startidx,endidx+1)]+[0.])
        return ImpulseResponse(TimeDescriptor(td[startidx],
            endidx-startidx+1,td.Fs),
            [x[k] for k in range(startidx,endidx+1)])
    def FirFilter(self):
        """FIR filter equivalent of impulse response for processing
        
        @return an instance of class FirFilter that can be convolved with a waveform
        """
        td=self.td
        return FirFilter(FilterDescriptor(1,-td.H*td.Fs,td.K-1),self.Values())