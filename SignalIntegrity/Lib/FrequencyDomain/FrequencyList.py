"""
 Frequency lists
 
 Deals efficiently with evenly spaced frequency lists that can be described by three
 simple numbers and unvenly spaced freqeuncy lists that must contain the list of
 frequencies themselves.  Not only can evenly spaced frequency lists be compressed
 in data size, we often must know if the frequencies are evenly spaced and it's easier
 to know that when it is that class type.
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

class FrequencyList(list):
    """base class for lists of frequencies."""
    def __init__(self,f=None):
        """Constructor

        Initializes a frequency list either from another frequency list or from
        a list of frequencies provided.
        @param f (optional) list of frequencies or instance of class FrequencyList
        """
        if isinstance(f,FrequencyList):
            list.__init__(self,f)
            self.N=f.N
            self.Fe=f.Fe
            self.m_EvenlySpaced=f.m_EvenlySpaced
        elif isinstance(f,list): self.SetList(f)
    def SetEvenlySpaced(self,Fe,N):
        """sets evenly spaced
        @param Fe float end frequency for the frequency list
        @param N integer number of points (-1) or the frequency list (i.e. the number of points
        in the new frequency list will be N+1.
        @return self
        @remark
        Initializes the frequency list to be evenly spaced with N+1 points from n=0..N where each
        frequency is f[n]=n/N*Fe
        """
        self.Fe=Fe
        self.N=int(N)
        list.__init__(self,[Fe/N*n for n in range(self.N+1)])
        self.m_EvenlySpaced=True
        return self
    def SetList(self,fl):
        """Initializes the frequency list with a list of frequencies.
        @param fl list of frequencies
        @return self
        @remark
        This will set the List to the list provided, N to the length -1, and Fe to the frequency of
        the last element in the list.  It will set m_EvenlySpaced False.
        @note although this initializer is meant to take a list of frequencies, it will also take
        an instance of class FrequencyList, as it mimics this list behavior.  In this case, it will
        install it as if the FrequencyList instance was simply a list of frequencies.
        """
        list.__init__(self,fl)
        self.N=len(fl)-1
        self.Fe=fl[-1]
        self.m_EvenlySpaced=False
        return self
    def EvenlySpaced(self): return self.m_EvenlySpaced
    """whether evenly spaced
    @returns boolean whether the list is evenly spaced.
    @note It checks this by examining the internal
    flag m_EvenlySpaced.  It does no actual check of the list of frequencies.
    """
    def Frequencies(self,unit=None):
        """Frequencies
        @param unit optional string containing unit to use
        @return list of frequencies in the frequency list in the unit specified
        @remark
        Valid units are:
        - GHz - each frequency element is divided by 1e9.
        - MHz - each frequency element is divided by 1e6.
        - kHz - each frequency element is divided by 1e3

        If no unit is supplied or if it's None, then the frequencies are provided as is.

        if the unit supplied is otherwise invalid, None is returned.
        """
        if unit == None:
            return list(self)
        elif isinstance(unit,float):
            return (self/unit).Frequencies()
        elif unit == 'GHz':
            return (self/1.e9).Frequencies()
        elif unit == 'MHz':
            return (self/1.e6).Frequencies()
        elif unit == 'kHz':
            return (self/1.e3).Frequencies()
    def CheckEvenlySpaced(self,epsilon=0.01):
        """checks and sets whether evenly spaced
        @param epsilon (optional) float difference tolerated in whether a frequency compared is the same.
        (Defaults to 0.01).
        @return boolean whether the frequency list is evenly spaced.
        @note if the m_EvenlySpaced internal variable indicates it's evenly spaced, it simply returns True.

        Checks the frequencies to see if they conform to N+1 frequencies with for n=0..N, each frequency
        in the list is f[n]=n/N*Fe within the epsilon.
        """
        if self.m_EvenlySpaced:
            return True
        for n in range(self.N+1):
            if abs(self[n]-self.Fe/self.N*n) > epsilon:
                self.m_EvenlySpaced=False
                return False
        self.SetEvenlySpaced(self.Fe,self.N)
        return True
    def __div__(self,d):
        return self.__truediv__(d)
    def __truediv__(self,d):
        """overloads /
        @param d float frequency to divide each frequency by.
        @return an instance of class FrequencyList containing self divided by the amount specified.
        """
        if self.EvenlySpaced():
            return EvenlySpacedFrequencyList(self.Fe/d,self.N)
        else:
            return GenericFrequencyList([v/d for v in self])
    def __mul__(self,d):
        """overloads *
        @param d float frequency to multiply each frequency by.
        @return an instance of class FrequencyList containing self multiplied by the amount specified.
        """
        if self.EvenlySpaced():
            return EvenlySpacedFrequencyList(self.Fe*d,self.N)
        else:
            return GenericFrequencyList([v*d for v in self])
    def TimeDescriptor(self,Keven=True):
        """associated time descriptor
        @param Keven boolean (optional)
        Whether N is from an even K points in the time domain (i.e. K/2) or from an odd K points in the time-domain
        (i.e. (K+1)/2).  Defaults to True.
        @return an instance of class TimeDescriptor that corresponds to the time descriptor that would
        generate this frequency descriptor.
        @note this is assumed to be a time descriptor that would produce a frequency descriptor with self's
        end frequency and number of points.  It does not check whether the list is evenly spaced."""
        # pragma: silent exclude
        from SignalIntegrity.Lib.TimeDomain.Waveform.TimeDescriptor import TimeDescriptor
        # pragma: include
        N=self.N
        K=2*N
        if not Keven: K=K+1
        Fs=self.Fe*K/N
        return TimeDescriptor(-K/2./Fs,K,Fs)
    def __eq__(self,other):
        """overloads ==
        @param other an other instance of class FrequencyList
        @return boolean True if the other is the same as self.
        @note the elements in the list are checked within an epsilon value of 1e-6.
        """
        if self.m_EvenlySpaced != other.m_EvenlySpaced:
            return False
        if self.N != other.N:
            return False
        if abs(self.Fe - other.Fe) > 1e-5:
            return False
        if not self.m_EvenlySpaced:
            for k in range(len(self)):
                if abs(self[k]-other[k])>1e-6:
                    return False
        return True
    def __ne__(self,other):
        """overloads !=
        @param other an other instance of class FrequencyList
        @return boolean True if the other is the same as self.
        @see __eq__()
        """
        return not self == other
    ##
    # @var N
    # integer number (-1) of frequency list elements (i.e. the number of frequency elements
    # is N+1.
    # @var Fe
    # float end frequency for the frequency list
    # @var m_EvenlySpaced
    # boolean whether the list of frequencies is evenly spaced

class EvenlySpacedFrequencyList(FrequencyList):
    """A evenly spaced list of frequencies"""
    def __init__(self,Fe,Np):
        """Constructor
        @param Fe float end frequency for the frequency list.
        @param Np integer number of points (-1) or the frequency list (i.e. the number of points.
        in the new frequency list will be N+1.
        @remark
        Initializes the frequency list to be evenly spaced with Np+1 points from n=0..Np where each
        frequency is f[n]=n/Np*Fe.
        """
        FrequencyList.__init__(self)
        self.SetEvenlySpaced(Fe,Np)

class GenericFrequencyList(FrequencyList):
    """A generic list of frequencies assumed to be not evenly spaced."""
    def __init__(self,fl):
        """Constructor
        @param fl list of frequencies.
        @return self.
        @remark
        Initializes the frequency list with a list of frequencies.

        This will set the List to the list provided, N to the length -1, and Fe to the frequency of
        the last element in the list.  It will set m_EvenlySpaced False.

        @note although this initializer is meant to take a list of frequencies, it will also take
        an instance of class FrequencyList, as it mimics this list behavior.  In this case, it will
        install it as if the FrequencyList instance was simply a list of frequencies.
        """
        FrequencyList.__init__(self)
        self.SetList(fl)
