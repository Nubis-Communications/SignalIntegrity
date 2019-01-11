"""
TimeDescriptor.py
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

from SignalIntegrity.Lib.TimeDomain.Filters.FilterDescriptor import FilterDescriptor
from SignalIntegrity.Lib.FrequencyDomain.FrequencyList import EvenlySpacedFrequencyList

class TimeDescriptor(object):
    """time-axis for waveforms"""
    def __init__(self,HorOffset,NumPts,SampleRate):
        """Constructor
        @param HorOffset float time of first point
        @param NumPts integer number of points
        @param SampleRate float sample rate (1/sample period)
        """
        self.H = HorOffset
        self.K = int(NumPts)
        self.Fs=SampleRate
    def __len__(self):
        """overloads len()
        @return number of time points
        """
        return self.K
    def __getitem__(self,item):
        """overloads [item]
        @param item integer or float index
        @return float time at the index item specified.
        """
        return item/self.Fs+self.H
    def __eq__(self,other):
        """overloads ==
        @param other instance of class TimeDescriptor
        @return boolean whether the other descriptor is the same.
        @note the sample rate is compared with an epsilon of 1e-15.
        @note the horizontal offset is compared with an epsilong of 0.001% of the sample period.
        """
        if abs(self.Fs - other.Fs) > 1e-15: return False
        if abs(self.H - other.H) > .00001*1./self.Fs: return False
        if self.K != other.K: return False
        return True
    def __ne__(self,other):
        """overloads !=
        @param other instance of class TimeDescriptor
        @return boolean whether other descriptor is not the same.
        @see TimeDescriptor.__eq__
        """
        return not self == other
    def Times(self,unit=None):
        """returns list of times
        @param unit (optional) string of units for time values.
        @return list of times corresponding to self.
        @note valid time units are:
        - None - return simply the list of time values.
        - 'ps' - return the time values divided by 1e-12.
        - 'ns' - return the time values divided by 1e-9.
        - 'us' - return the time values divided by 1e-6.
        - 'ms' - return the time values divided by 1e-3.
        """
        if unit==None:
            return [self[k] for k in range(len(self))]
        elif isinstance(unit,float):
            return [self[k]/unit for k in range(len(self))]
        elif unit=='ps':
            return [self[k]/1.e-12 for k in range(len(self))]
        elif unit=='ns':
            return [self[k]/1.e-9 for k in range(len(self))]
        elif unit =='us':
            return [self[k]/1.e-6 for k in range(len(self))]
        elif unit == 'ms':
            return [self[k]/1.e-3 for k in range(len(self))]
    def ApplyFilter(self,F):
        """calculates effect of filter

        calculates the new time descriptor of a waveform filtered by a filter
        with the filter descriptor provided.

        @param F instance of class FilterDescriptor
        @return instance of class TimeDescriptor containing the time descriptor
        affected by the filter.
        @note does not affect self.
        """
        return TimeDescriptor(
            HorOffset=self.H+(F.S-F.D)/self.Fs,
            NumPts=int(max(0,(self.K-F.S)*F.U)),
            SampleRate=self.Fs*F.U)
    def __mul__(self,F):
        """overloads *

        This is an abstraction

        calculates the new time descriptor of a waveform filtered by a filter
        with the filter descriptor provided.

        @param F instance of class FilterDescriptor
        @return instance of class TimeDescriptor containing the time descriptor
        affected by the filter.
        @note does not affect self.
        @see ApplyFilter()
        """
        return self.ApplyFilter(F)
    def __div__(self,other):
        return self.__truediv__(other)
    def __truediv__(self,other):
        """overloads /

        This is an abstraction and is polymorphic.

        if other is a filter descriptor, it assumes self is an outputwf such that
        inputwf*other=outputwf and it calculates the inputwf  as outputwf*other^-1.
        This is the same as finding the input waveform that if filtered by other would
        produce self.

        if other is an input wf time descriptor, it assume that self is an output wf such that
        inputwf*filter=outputwf and it calculates the filter as inputwf^-1*outputwf.
        This is the same as finding the filter that, when applied to other, would produce self.
        
        @param other instance of class TimeDescriptor or FilterDescriptor.
        @return instance of class TimeDescriptor or FilterDescriptor depending on the situations
        explained.
        """
        if isinstance(other,FilterDescriptor):
            return TimeDescriptor(
                HorOffset=self.H+other.U/self.Fs*(other.D-other.S),
                NumPts=self.K/other.U+other.S,
                SampleRate=self.Fs/other.U)
        elif isinstance(other,TimeDescriptor):
            UpsampleFactor=self.Fs/other.Fs
            return FilterDescriptor(
                UpsampleFactor,
                DelaySamples=other.K-self.K/UpsampleFactor-
                    (self.H-other.H)*other.Fs,
                StartupSamples=other.K-self.K/UpsampleFactor)
    def DelayBy(self,D):
        """delays by time
        @param D float delay time
        @return instance of class TimeDescriptor containing self delayed by the time.
        @note does not affect self.
        """
        return TimeDescriptor(self.H+D,self.K,self.Fs)
    def FrequencyList(self):
        """corresponding frequency list

        calculates a list of frequencies for a frequency domain waveform that would correspond
        to the time descriptor self.

        @return instance of EvenlySpacedFrequencyList containing list of frequencies that
        correspond to this time descriptor.
        """
        K=int(self.K)
        N=K//2
        Fe=float(self.Fs)*N/K
        return EvenlySpacedFrequencyList(Fe,N)
    def Intersection(self,other):
        """intersection of two waveforms

        The intersection is the portion of two time-axes that overlap

        @param other instance of class TimeDescriptor
        @return the intersection of the two waveform descriptors
        """
        return TimeDescriptor(
            HorOffset=max(self.H,other.H),
            NumPts=max(0,min(self.TimeOfPoint(self.K),
                other.TimeOfPoint(other.K))-max(self.H,other.H))*self.Fs,
            SampleRate=self.Fs)
    def TimeOfPoint(self,k):
        """time corresponding to point index
        @param k integer (or float) index of time point
        @return float time of that point
        @note the index can be fractional
        @note the index does not have to correspond to a point inside the list of times.
        """
        return self.H+float(k)/self.Fs
    def IndexOfTime(self,t,Integer=True):
        """point index corresponding to time
        @param t float time of point
        @param Integer (optional, defaults to True) whether to return nearest integer.
        Otherwise, returns float with possible fractional index
        @return index of point corresponding to time
        @note the index may not correspond to a point inside the list of times.
        """
        index=(t-self.H)*self.Fs
        if Integer: index=int(index)
        return index
    def Print(self):
        """prints an ascii version of the time descriptor"""
        print('HorOffset:  '+str(self.H))
        print('NumPts:     '+str(self.K))
        print('SampleRate: '+str(self.Fs))
