"""
 Frequency Domain Base Class
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

import math
import cmath
import sys

import numpy as np

from SignalIntegrity.Lib.FrequencyDomain.FrequencyList import FrequencyList
from SignalIntegrity.Lib.FrequencyDomain.FrequencyList import EvenlySpacedFrequencyList
from SignalIntegrity.Lib.FrequencyDomain.FrequencyList import GenericFrequencyList

class FrequencyDomain(object):
    """base class for frequency domain elements.  This class handles all kinds of utility things
    common to all frequency-domain classes.
    @note the complex frequency-domain values are stored internally as a numpy
    array (`self.values`); the class provides a sequence-like interface and numpy
    interoperability via `__array__`.
    """
    def __init__(self,f=None,resp=None):
        """Constructor
        @param f (optional) instance of class FrequencyList
        @param resp (optional) numpy array/list of complex frequency content or response
        """
        self.m_f=FrequencyList(f)
        if resp is not None:
            self.values=np.asarray(resp,dtype=complex)
        else:
            self.values=np.array([],dtype=complex)
    def __len__(self):
        return len(self.values)
    def __getitem__(self,index):
        return self.values[index]
    def __setitem__(self,index,value):
        self.values[index]=value
    def __iter__(self):
        return iter(self.values)
    def __repr__(self):
        """value-based representation (matches the historical list representation)
        @return repr of the complex values as a python list
        @note deterministic and value-based so it can be used in results-cache hash
        computations; the default object repr would embed a memory address and break caching.
        """
        return repr(self.values.tolist())
    def __array__(self,dtype=None,copy=None):
        """numpy array interface returning the internal complex values array"""
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
    def FrequencyList(self):
        """FrequencyList
        @return the frequency list in m_f
        """
        return self.m_f
    def Frequencies(self,unit=None):
        """Frequencies
        @param unit (optional) string containing the unit for the frequencies
        @see FrequencyList for information on valid unit strings.
        """
        return self.m_f.Frequencies(unit)
    def Values(self,unit=None):
        """Values
        @param unit (optional) string containing the unit for the frequencies
        @return numpy array of complex values (when no unit is specified) or a list of
        float values (for a specified unit) corresponding to the frequency-domain elements in the
        units specified.
        @remark
        Valid unit strings are:
        - 'dB' - values in decibels.
        - 'mag' - values in absolute magnitude.
        - 'rad' - the argument or phase in radians.
        - 'deg' - the argument or phase in degrees.
        - 'real' - the real part of the values.
        - 'imag' - the imaginary part of the values.

        Returns a numpy array of complex values if no unit specified.

        Returns None if the unit is invalid.
        """
        if unit==None:
            return self.values.copy()
        elif unit =='dB':
            mag=np.abs(self.values)
            result=np.full(len(mag),-3000.)
            nonzero=mag>=1e-15
            result[nonzero]=20.*np.log10(mag[nonzero])
            return result.tolist()
        elif unit == 'mag':
            return np.abs(self.values).tolist()
        elif unit == 'rad':
            return np.angle(self.values).tolist()
        elif unit == 'deg':
            return np.degrees(np.angle(self.values)).tolist()
        elif unit == 'real':
            return self.values.real.tolist()
        elif unit == 'imag':
            return self.values.imag.tolist()
    def ReadFromLines(self,data):
        """reads in frequency domain content from the lines specified.
        @param data list of lines to read from
        @return self
        """
        if data is None or len(data) == 0:
            FrequencyDomain.__init__(self)
            return self
        if data[0].strip('\n')!='UnevenlySpaced':
            N = int(str(data[0]))
            Fe = float(str(data[1]))
            frl=[line.strip().split(' ') for line in data[2:]]
            resp=[float(fr[0])+1j*float(fr[1]) for fr in frl]
            self.m_f=EvenlySpacedFrequencyList(Fe,N)
            self.values=np.asarray(resp,dtype=complex)
        else:
            frl=[line.split(' ') for line in data[1:]]
            f=[float(fr[0]) for fr in frl]
            resp=[float(fr[1])+1j*float(fr[2]) for fr in frl]
            self.m_f=GenericFrequencyList(f)
            self.values=np.asarray(resp,dtype=complex)
        return self
    def ReadFromFileStream(self,f):
        """reads in frequency domain content from the file stream specified.
        @param f file stream to read from
        @return self
        """
        data=f.readlines()
        self.ReadFromLines(data)
        return self
    def ReadFromFile(self,fileName):
        """reads in frequency domain content from the file specified.
        @param fileName string file name to read
        @return self
        """
        with open(fileName,'rU' if sys.version_info.major < 3 else 'r') as f:
            self.ReadFromFileStream(f)
        return self
    def WriteToFileStream(self,f):
        """write the frequency domain content to the file stream specified.
        @param f file stream to write to
        @return self
        """
        fl=self.FrequencyList()
        if fl.CheckEvenlySpaced():
            f.write(str(fl.N)+'\n')
            f.write(str(fl.Fe)+'\n')
            for v in self.Values():
                f.write(str(v.real)+' '+str(v.imag)+'\n')
        else:
            f.write('UnevenlySpaced\n')
            for n in range(len(fl)):
                f.write(str(fl[n])+' '+str(self.Values()[n].real)+' '+
                str(self.Values()[n].imag)+'\n')
        return self
    def WriteToFile(self,fileName):
        """write the frequency domain content to the file specified.
        @param fileName string file name to write
        @return self
        """
        with open(fileName,"w") as f:
            self.WriteToFileStream(f)
        return self
    def __eq__(self,other):
        """overloads ==
        @param other an instance of a class derived from FrequencyDomain.
        @return whether self == other
        """
        if self.FrequencyList() != other.FrequencyList():
            return False # pragma: no cover
        if len(self) != len(other):
            return False # pragma: no cover
        if np.any(np.abs(self.values - np.asarray(other)) > 1e-5):
            return False # pragma: no cover
        return True
    def __ne__(self,other):
        """overloads !=
        @param other an instance of a class derived from FrequencyDomain.
        @return whether self != other
        """
        return not self == other
    def LimitEndFrequency(self,endFrequency):
        """limits the end frequency
        @param endFrequency float end frequency to limit to
        @return self
        @remark if the end frequency is higher than the current end frequency,
        the content is left unchanged.
        @warning the end frequency might be slightly higher and this is not
        a strict limit.  The goal is for the frequencies to potentially bracket
        the desired end frequency.
        """
        frequencies=self.Frequencies()
        deltaf=frequencies[-1]/(len(self)-1)
        numPts=int(math.ceil(endFrequency/deltaf))
        if numPts >= len(self):
            return self
        fl=FrequencyList(frequencies[0:numPts+1])
        fl.CheckEvenlySpaced()
        FrequencyDomain.__init__(self,fl,self[0:numPts+1])
        return self
    def __div__(self,other):
        return self.__truediv__(other)
    def __truediv__(self,other):
        """overloads /
        @param other object of type FrequencyDomain
        @return the frequency domain division of self and other (does not affect self)
        """
        import copy
        rv=copy.deepcopy(self)
        rv.__init__(self.Frequencies(),self.values/np.asarray(other))
        return rv
    def __mul__(self,other):
        """overloads *
        @param other object of type FrequencyDomain
        @return the frequency domain multiplication of self and other (does not affect self)
        """
        import copy
        rv=copy.deepcopy(self)
        rv.__init__(self.Frequencies(),self.values*np.asarray(other))
        return rv

    ##
    # @var m_f
    # instance of class FrequencyList
