"""
 Noise density
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

from SignalIntegrity.Lib.FrequencyDomain.FrequencyDomain import FrequencyDomain
from SignalIntegrity.Lib.ToSI import FromSI

class NoiseDensity(FrequencyDomain):
    def __init__(self, f=None, resp=None, unit1=None, unit2=None):
        FrequencyDomain.__init__(self, f=f, resp=resp)
    @static_method
    def UnitSplit(unit):
        unit1,unit2=unit.strip().split('/').strip()
        unit1_valid = False
        # unit 1 (values)
        try:
            unit1_multiplier = FromSI('1'+unit1)
            if unit1_multiplier is None:
                return None # can't convert the number
            if unit1 == 'dBm':
                unit1_type = 'dBm'
            elif unit1[-1] in ['V','A']:
                unit1_type = 'V'
            elif unit1[-3:] in ['V^2','A^2']:
                unit1_type = 'V^2'
            else:
                raise Exception
        except:
            return None # neither dBm, V, A, V^2, or A^2
        # unit 2 (frequency)
        try:
            try:
                unit2_unit = unit2.split('sqrt(')[1].split(')')[0].strip()
                unit2_type = 'sqrt(Hz)'
            except:
                unit2_type = 'Hz'

            if not unit2_unit[-2:] != 'Hz':
                raise Exception

            unit2_multiplier = FromSI('1'+unit2_unit)
            if unit2_multiplier is None:
                raise Exception
            unit2_valid = True
        except:
            return None # not in units 'per sqrt(Hz)' or 'per Hz' 


    @static_method
    def Convert(value,unit_initial,unit_final):
        pass
    def Values(self,unit=None):
        """Values
        @param unit1 (optional) string containing the unit for the values.
        @return list of complex values corresponding to the noise elements in the
        units specified.
        @remark
        unit strings are assumed to contain two actual strings separated by a '/'.  As such,
        unit = unit1/unit2.

        Valid unit1 strings are:
        - 'dBm' - values in dBm.
        - 'a,f,p,n,u,m,k,M,G, or T' followed by 'V or A' - values in V or A rms.
        - 'a,f,p,n,u,m,k,M,G,or T' followed by 'V^2 or A^2' - values in V^2 or A^2 rms.
        Valid unit2 strings are:
        - 'a,f,p,n,u,m,k,M,G,or T' followed by 'Hz' - values in Hz
        - 'sqrt(' followed by 'a,f,p,n,u,m,k,M,G, or T' followed by 'Hz)' - values in sqrt(Hz)

        since values are stored internally in V/sqrt(Hz), if no unit1 or unit2 is supplied, these are the units
        of the values returned.

        Returns the list of complex values if no unit specified.

        Returns None if the unit1 or unit2 is invalid.
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
