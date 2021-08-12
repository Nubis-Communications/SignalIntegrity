"""
 Impulse Response Filter
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

from SignalIntegrity.Lib.SParameters.SParameters import SParameters
from SignalIntegrity.Lib.TimeDomain.Waveform.Waveform import Waveform
from SignalIntegrity.Lib.TimeDomain.Waveform.ImpulseResponse import ImpulseResponse
from SignalIntegrity.Lib.Exception import SignalIntegrityExceptionWaveformFile

class ImpulseResponseFilter(SParameters):
    """class for impulse response filter"""
    def __init__(self,filename,wfProjName=None,normalizedDCGain=None,multiplyByTs=True,derivative=False):
        """Constructor
        @param filename string file name of s-parameter file to read.
        @param normalizedDCGain (optional, defaults to None) DC gain to normalize response to.
        @param multiplyByTs (optional, defaults to True) whether to multiply the waveform by the sample period
        @param derivative (optional, defaults to False) whether to use the derivative of the waveform

        Reads the waveform file and produces SParameters.

        The s-parameters are for a two-port device that is "amplifier-like", meaning it has infinite
        input impedance, zero output impedance, the impulse response forms s21, and has infinite reverse
        isolation.

        If normalizedDCGain is 0 or None, the DC gain is not normalized, otherwise the filter is normalized by setting
        the sum of the values in the impulse response equal to this gain value.

        if multiplyByTs is True, it assumes that the impulse response waveform is an ordinary waveform, and the impulse
        response is formed by multiplying every value by the sample period.

        if derivative is True, the derivative of the waveform is taken.  This is useful when you are provided a step
        response.
        """
        ext=str.lower(filename).split('.')[-1]
        if ext == 'si':
            from SignalIntegrity.App.SignalIntegrityAppHeadless import ProjectWaveform
            wf=ProjectWaveform(filename,wfProjName)
            if wf == None:
                raise SignalIntegrityExceptionWaveformFile('waveform could not be produced by '+filename)
        else:
            try:
                wf=Waveform().ReadFromFile(filename)
            except:
                raise SignalIntegrityExceptionWaveformFile('waveform could not be produced by '+filename)
        if derivative:
            wf=wf.Derivative()
        if multiplyByTs:
            wf=wf*(1./wf.TimeDescriptor().Fs)
        if not ((normalizedDCGain == None) or (normalizedDCGain == 0)):
            wf=wf*(1./sum(wf))
        fr=ImpulseResponse(wf).FrequencyResponse()
        fl=fr.Frequencies()
        SParameters.__init__(self,fl,[[[1.,0],[2.*r,-1]] for r in fr])