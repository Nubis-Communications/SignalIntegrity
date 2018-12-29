"""
 Frequency Domain Base Class
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
    ##
    # @var m_f
    # instance of class FrequencyList
