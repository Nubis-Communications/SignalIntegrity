"""
FilterDescriptor.py
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

class FilterDescriptor(object):
    """handles time axis effects of filtering"""
    def __init__(self,UpsampleFactor,DelaySamples,StartupSamples):
        """Constructor
        @param UpsampleFactor integer or float upsample factor.  This is the multiplicative
        factor that the filter will have on the sample rate of an applied waveform.
        @param DelaySamples integer or float samples that the filter applies to a waveform.
        @param StartupSamples integer or float the number of samples that must be removed from
        the  filtered waveform due to filter startup effects.
        """
        self.U = UpsampleFactor
        self.D = DelaySamples
        self.S = StartupSamples
    def __eq__(self,other):
        """overloads ==
        @return boolean whether to filter descriptors are the same
        """
        if abs(self.U - other.U) > 1e-15: return False
        if abs(self.D - other.D) > 1e-15: return False
        if abs(self.S - other.S) > 1e-15: return False
        return True
    def __mul__(self,other):
        """overloads *\n
        multiplies two filter descriptors.  This is the same as calculating the
        effect of the two filters in cascade.
        @param other an instance of class FilterDescriptor of another filter
        @return instance of class FilterDescriptor of the cascaded filters
        """
        if isinstance(other,FilterDescriptor):
            return FilterDescriptor(
                UpsampleFactor=self.U*other.U,
                DelaySamples=float(self.U*self.D+other.D)/self.U,
                StartupSamples=float(self.U*self.S+other.S)/self.U)
    def Before(self,other):
        """calculates the effect of another filter before this one.
        @param other an instance of class FilterDescriptor of another filter
        @return instance of class FilterDescriptor of the other filter moved before this one
        """
        return FilterDescriptor(
                UpsampleFactor=self.U,
                DelaySamples=(other.D*other.U+self.D)/other.U-other.D/self.U,
                StartupSamples=(other.U*other.S+self.S)/other.U-other.S/self.U)
    def After(self,other):
        """calculates the effect of another filter after this one.
        @param other an instance of class FilterDescriptor of another filter
        @return instance of class FilterDescriptor of the other filter moved after this one
        """
        return FilterDescriptor(
                UpsampleFactor=self.U,
                DelaySamples=(self.D*self.U+other.D)*other.U/self.U-other.D*other.U,
                StartupSamples=(self.S*self.U+other.S)*other.U/self.U-other.U*other.S)
    def TrimLeft(self):
        """waveform points trimmed from the left
        @return the number of waveform points trimmed from the left by applying this filter
        """
        return self.S-self.D
    def TrimRight(self):
        """waveform points trimmed from the right
        @return the number of waveform points trimmed from the right by applying this filter
        """
        return self.D
    def TrimTotal(self):
        """waveform points trimmed in total
        @return the total number of waveform points trimmed by applying this filter
        """
        return self.S
    def Print(self):
        """prints the filter descriptor in ASCII"""
        print('UpsampleFactor: '+str(self.U))
        print('DelaySamples:   '+str(self.D))
        print('StartupSamples: '+str(self.S))
        print('TrimLeft:       '+str(self.TrimLeft()))
        print('TrimRight:      '+str(self.TrimRight()))
        print('TrimTotal:      '+str(self.TrimTotal()))
