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

from SignalIntegrity.Lib.FrequencyDomain.FrequencyList import FrequencyList
from SignalIntegrity.Lib.FrequencyDomain.FrequencyList import EvenlySpacedFrequencyList
from SignalIntegrity.Lib.FrequencyDomain.FrequencyList import GenericFrequencyList

class FrequencyDomain(list):
    """base class for frequency domain elements.  This class handles all kinds of utility things
    common to all frequency-domain classes.
    """
    def __init__(self,f=None,resp=None):
        """Constructor
        @param f (optional) instance of class FrequencyList
        @param resp (optional) list of complex frequency content or response
        """
        self.m_f=FrequencyList(f)
        if not resp is None:
            list.__init__(self,resp)
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
        @return list of complex values corresponding to the frequency-domain elements in the
        units specified.
        @remark
        Valid unit strings are:
        - 'dB' - values in decibels.
        - 'mag' - values in absolute magnitude.
        - 'rad' - the argument or phase in radians.
        - 'deg' - the argument or phase in degrees.
        - 'real' - the real part of the values.
        - 'imag' - the imaginary part of the values.

        Returns the list of complex values if no unit specified.

        Returns None if the unit is invalid.
        """
        if unit==None:
            return list(self)
        elif unit =='dB':
            return [-3000. if (abs(self[n]) < 1e-15) else
                     20.*math.log10(abs(self[n]))
                        for n in range(len(self.m_f))]
        elif unit == 'mag':
            return [abs(self[n]) for n in range(len(self.m_f))]
        elif unit == 'rad':
            return [cmath.phase(self[n]) for n in range(len(self.m_f))]
        elif unit == 'deg':
            return [cmath.phase(self[n])*180./math.pi
                        for n in range(len(self.m_f))]
        elif unit == 'real':
            return [self[n].real for n in range(len(self.m_f))]
        elif unit == 'imag':
            return [self[n].imag for n in range(len(self.m_f))]
    def ReadFromFile(self,fileName):
        """reads in frequency domain content from the file specified.
        @param fileName string file name to read
        @return self
        """
        with open(fileName,'rU' if sys.version_info.major < 3 else 'r') as f:
            data=f.readlines()
        if data[0].strip('\n')!='UnevenlySpaced':
            N = int(str(data[0]))
            Fe = float(str(data[1]))
            frl=[line.split(' ') for line in data[2:]]
            resp=[float(fr[0])+1j*float(fr[1]) for fr in frl]
            self.m_f=EvenlySpacedFrequencyList(Fe,N)
            list.__init__(self,resp)
        else:
            frl=[line.split(' ') for line in data[1:]]
            f=[float(fr[0]) for fr in frl]
            resp=[float(fr[1])+1j*float(fr[2]) for fr in frl]
            self.m_f=GenericFrequencyList(f)
            list.__init__(self,resp)
        return self
    def WriteToFile(self,fileName):
        """write the frequency domain content to the file specified.
        @param fileName string file name to write
        @return self
        """
        fl=self.FrequencyList()
        with open(fileName,"w") as f:
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
    def __eq__(self,other):
        """overloads ==
        @param other an instance of a class derived from FrequencyDomain.
        @return whether self == other
        """
        if self.FrequencyList() != other.FrequencyList():
            return False # pragma: no cover
        if len(self) != len(other):
            return False # pragma: no cover
        for k in range(len(self)):
            if abs(self[k] - other[k]) > 1e-5:
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
        rv.__init__(self.Frequencies(),[sd/od for sd,od in zip(self.Values(),other.Values())])
        return rv
    def __mul__(self,other):
        """overloads *
        @param other object of type FrequencyDomain
        @return the frequency domain multiplication of self and other (does not affect self)
        """
        import copy
        rv=copy.deepcopy(self)
        rv.__init__(self.Frequencies(),[sd*od for sd,od in zip(self.Values(),other.Values())])
        return rv
    def FixDCPhase(self,dc_phase_deg=0,min_abs=0.001):
        """Fixes the DC phase  
        Usually, frequency responses start with a phase of zero or 180 degrees.
        If this is not the case, real valued waveforms are not possible.  This fixes the DC point.
        @param dc_phase_deg float, defaults to 0, phase to set the DC point to.  180 or 0 are the only real logical choices.
        @return self (with dc phases fixed)
        @remark phases are only fixed in off diagonal elements by unwrapping the phase, moving the phase up or down, and restoring
        the phase delay
        @note this function raises an exception if there is no DC point already, or the points are not evenly spaced.
        """
        if self.m_f.CheckEvenlySpaced():
            if abs(self[0]) > min_abs:
                deg_list=self.Response('deg')
                phase_delta=dc_phase_deg-deg_list[0]
                fr_list=[m*cmath.exp(1j*(d+phase_delta)*math.pi/180.) for m,d in zip(self.Response('mag'),deg_list)]
                list.__init__(self,fr_list)
        return self
    def PrincipalDelay(self,fd=True):
        """Returns the principal delay of the impulse response  
        The principal delay is the location of the largest absolute value of the impulse response waveform.
        @return the principal delay
        """
        TD=0
        if fd or not self.m_f.CheckEvenlySpaced():
            # perform the calculation in the frequency domain
            if len(self)>=3:
                deg=[cmath.phase(v) for v in self]
                ddeg = [0 for _ in range(len(self)-1)]
                nn_range=range(1,len(self)-1)
                for nn in nn_range:
                    ddegf=(deg[nn]-deg[nn-1])/(2.*math.pi*(self.m_f[nn]-self.m_f[nn-1]))
                    ddegb=(deg[nn+1]-deg[nn])/(2.*math.pi*(self.m_f[nn+1]-self.m_f[nn]))
                    ddeg[nn]=ddegb if abs(ddegf) >= abs(ddegb) else ddegf
                W=[abs(v) for v in self]
                try:
                    TD=-sum([W[nn]*ddeg[nn] for nn in nn_range])/sum([W[nn] for nn in nn_range])
                except:
                    pass
        else:
            ir=self.ImpulseResponse()
            if ir is not None:
                TD=ir.PrincipalDelay()
        return TD
    ##
    # @var m_f
    # instance of class FrequencyList
