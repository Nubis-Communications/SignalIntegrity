"""
 Frequency Response Filter
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

from SignalIntegrity.Lib.SParameters.SParameters import SParameters
from SignalIntegrity.Lib.FrequencyDomain.FrequencyResponse import FrequencyResponse
from SignalIntegrity.Lib.Exception import SignalIntegrityExceptionWaveformFile

class FrequencyResponseFilter(SParameters):
    """class for frequency response filter"""
    def __init__(self,filename,normalizedDCGain=None,**kwargs):
        """Constructor
        @param filename string file name of frequency response file to read.
        @param normalizedDCGain float (optional, defaults to None) DC gain to normalize response to.
        @param **kwargs dict (optional, defaults to {}) dictionary of arguments for the file

        Reads the frequency response file directly and produces SParameters.

        The s-parameters are for a two-port device that is "amplifier-like", meaning it has infinite
        input impedance, zero output impedance, the frequency response forms s21, and has infinite reverse
        isolation.

        If normalizedDCGain is 0 or None, the DC gain is not normalized, otherwise the filter is normalized
        by setting the DC value of the frequency response equal to unity.
        """
        try:
            fr=FrequencyResponse().ReadFromFile(filename)
        except:
            raise SignalIntegrityExceptionWaveformFile('frequency response could not be produced by '+filename)
        if not ((normalizedDCGain == None) or (normalizedDCGain == 0)):
            fr=FrequencyResponse(fr.Frequencies(),[r/fr[0] for r in fr])
        fl=fr.Frequencies()
        SParameters.__init__(self,fl,[[[1.,0],[2.*r,-1]] for r in fr])
