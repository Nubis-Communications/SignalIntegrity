"""
 Frequency lists
 
 Deals efficiently with evenly spaced frequency lists that can be described by three
 simple numbers and unvenly spaced freqeuncy lists that must contain the list of
 frequencies themselves.  Not only can evenly spaced frequency lists be compressed
 in data size, we often must know if the frequencies are evenly spaced and it's easier
 to know that when it is that class type.
"""

# Copyright (c) 2021 Nubis Communications, Inc.
# Copyright (c) 2018-2020 Teledyne LeCroy, Inc.
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

import numpy as np

class FrequencyList(object):
    """base class for lists of frequencies.
    @note the frequencies are stored internally as a one-dimensional numpy array
    (`self.values`); the class provides a sequence-like interface (indexing,
    iteration, len) and numpy interoperability via `__array__`.
    """
    def __init__(self,f=None):
        """Constructor  
        Initializes a frequency list either from another frequency list or from
        a list/array of frequencies provided.
        @param f (optional) list/numpy array of frequencies or instance of class FrequencyList
        """
        if isinstance(f,FrequencyList):
            self.values=np.array(f.values,copy=True)
            self.N=f.N
            self.Fe=f.Fe
            self.m_EvenlySpaced=f.m_EvenlySpaced
        elif f is not None:
            self.SetList(f)
        else:
            self.values=np.array([],dtype=float)
    def __len__(self):
        """@return int number of frequencies in the list"""
        return len(self.values)
    def __getitem__(self,index):
        """indexing into the frequency list
        @param index int index or slice
        @return a Python float for an int index (so downstream per-frequency
        device math keeps Python scalar-division semantics, e.g. ZeroDivisionError
        at DC), or a numpy array for a slice
        """
        if isinstance(index,(int,np.integer)):
            return float(self.values[index])
        return self.values[index]
    def __setitem__(self,index,value):
        self.values[index]=value
    def __iter__(self):
        return iter(self.values)
    def __array__(self,dtype=None,copy=None):
        """numpy array interface returning the internal frequency values array
        @param dtype (optional) requested numpy dtype
        @param copy (optional) numpy 2.0 copy semantics
        """
        arr=self.values if dtype is None else self.values.astype(dtype)
        if copy:
            arr=np.array(arr,copy=True)
        return arr
    def __copy__(self):
        n=self.__class__.__new__(self.__class__)
        n.__dict__.update(self.__dict__)
        n.values=np.array(self.values,copy=True)
        return n
    def __deepcopy__(self,memo):
        from copy import deepcopy
        n=self.__class__.__new__(self.__class__)
        for k,v in self.__dict__.items():
            n.__dict__[k]=deepcopy(v,memo)
        return n
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
        self.values=(Fe/N)*np.arange(self.N+1)
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
        self.values=np.asarray(fl,dtype=float)
        self.N=len(self.values)-1
        self.Fe=self.values[-1]
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
        @remark Valid units are:
        - GHz - each frequency element is divided by 1e9.
        - MHz - each frequency element is divided by 1e6.
        - kHz - each frequency element is divided by 1e3

        If no unit is supplied or if it's None, then the frequencies are provided as is.

        if the unit supplied is otherwise invalid, None is returned.
        """
        if unit == None: return self.values.copy()
        elif isinstance(unit,float): return (self/unit).Frequencies()
        elif unit == 'GHz': return (self/1.e9).Frequencies()
        elif unit == 'MHz': return (self/1.e6).Frequencies()
        elif unit == 'kHz': return (self/1.e3).Frequencies()
    def CheckEvenlySpaced(self,epsilon=0.01):
        """checks and sets whether evenly spaced
        @param epsilon (optional) float difference tolerated in whether a frequency compared is the same.
        (Defaults to 0.01).
        @return boolean whether the frequency list is evenly spaced.
        @note if the m_EvenlySpaced internal variable indicates it's evenly spaced, it simply returns True.

        Checks the frequencies to see if they conform to N+1 frequencies with for n=0..N, each frequency
        in the list is f[n]=n/N*Fe within the epsilon.
        """
        if self.m_EvenlySpaced: return True
        for n in range(self.N+1):
            try:
                if abs(self[n]-self.Fe/self.N*n) > epsilon:
                    self.m_EvenlySpaced=False
                    return False
            except:
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
        if self.EvenlySpaced(): return EvenlySpacedFrequencyList(self.Fe/d,self.N)
        else: return GenericFrequencyList([v/d for v in self])
    def __mul__(self,d):
        """overloads *
        @param d float frequency to multiply each frequency by.
        @return an instance of class FrequencyList containing self multiplied by the amount specified.
        """
        if self.EvenlySpaced(): return EvenlySpacedFrequencyList(self.Fe*d,self.N)
        else: return GenericFrequencyList([v*d for v in self])
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
        if self.m_EvenlySpaced != other.m_EvenlySpaced: return False
        if self.N != other.N: return False
        if abs(self.Fe - other.Fe) > 1e-5: return False
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

class LogarithmicallySpacedFrequencyList(FrequencyList):
    """a logarithmically spaced frequency list"""
    def __init__(self,start_frequency,end_frequency,points_per_decade):
        """Constructor
        @param start_frequency float start frequency
        @param end_frequency float end frequency
        @param points_per_decade integer number of points per decade
        Intitializes the frequency list with the list of frequencies

        The list of frequencies is constructed by first determining the list of frequencies in a decade based
        on the number of points per decade specified.  Then, for each decade, all of the points are retained
        that are above the start frequency and below the end frequency.  Finally, the start and end frequencies
        are tacked onto the list.
        """
        import math
        decade_list = [10.**(k/points_per_decade) for k in range(points_per_decade+1)]
        frequency_list=[start_frequency]
        for d in range(math.floor(math.log10(start_frequency)),math.ceil(math.log10(end_frequency))):
            for k in range(points_per_decade+1):
                this_frequency = decade_list[k] * math.pow(10.,d)
                if (this_frequency > frequency_list[-1]) and (this_frequency < end_frequency):
                    frequency_list.append(this_frequency)
        if end_frequency > frequency_list[-1]:
            frequency_list.append(end_frequency)
        FrequencyList.__init__(self,frequency_list)
