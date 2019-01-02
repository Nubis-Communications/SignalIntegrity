"""
 Frequency content
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

from numpy import fft

from SignalIntegrity.Lib.Exception import SignalIntegrityExceptionWaveform
from SignalIntegrity.Lib.FrequencyDomain.FrequencyDomain import FrequencyDomain
from SignalIntegrity.Lib.TimeDomain.Waveform.Waveform import Waveform
from SignalIntegrity.Lib.TimeDomain.Waveform.SineWaveform import SineWaveform
from SignalIntegrity.Lib.ChirpZTransform.ChirpZTransform import CZT
from SignalIntegrity.Lib.TimeDomain.Waveform.TimeDescriptor import TimeDescriptor

class FrequencyContent(FrequencyDomain):
    """Handles frequency content of waveforms.

    This is the frequency content view of a waveform.  In other words, it assumes that a waveform is an actual waveform and
    contains the complex values of sinusoids that, if added together, would make up the waveform.  This is the
    opposite of the FrequencyResponse() view.

    @see FrequencyResponse
    """
    R=50.0
    P=1e-3
    LogRP10=10.*math.log10(R*P)
    dB3=20*math.log10(math.sqrt(2))
    dB6=20*math.log10(0.5)
    def __init__(self,wf,fd=None):
        """Constructor
        @param wf in instance of class Waveform
        @param fd (optional) an instance of class FrequencyList (defaults to None)
        @remark
        initializes itself internally by computing the frequency content of the waveform.

        If fd is None then the frequency descriptor is simply the frequency descriptor corresponding to the time
        descriptor of the waveform and the frequency content is computed from the DFT.

        Otherwise, the CZT is used to compute the frequency content and the time descriptor corresponds to the
        frequency descriptor.

        the time descriptor and frequency descriptor are retained so a waveform can be obtained from the frequency content.

        @note the frequency content is scaled differently from the raw DFT or CZT outputs in that the absolute value of each
        complex number in the frequency content represents the amplitude of a cosine wave.  This is not true with the raw
        DFT output and scaling things this way helps in the proper interpretation of the frequency content without having
        to think about the vagaries of the DFT.

        @see TimeDescriptor
        @see FrequencyList
        @see ChirpZTransform
        """
        td=wf.td
        if fd is None:
            X=fft.fft(wf.Values())
            K=int(td.K)
            Keven=(K//2)*2 == K
            fd=td.FrequencyList()
        else:
            # pragma: silent exclude
            if not fd.EvenlySpaced():
                raise SignalIntegrityExceptionWaveform('cannot generate frequency content')
            # pragma: include
            K=fd.N*2
            Keven=True
            X=CZT(wf.Values(),td.Fs,0,fd.Fe,fd.N,True)
            td=TimeDescriptor(td.H,fd.N*2,fd.Fe*2.)
        FrequencyDomain.__init__(self,fd,[X[n]/K*\
            (1. if (n==0 or ((n==fd.N) and Keven)) else 2.)*\
            cmath.exp(-1j*2.*math.pi*fd[n]*td.H) for n in range(fd.N+1)])
        self.td=td
    def Values(self,unit=None):
        """frequency content values
        @param unit (optional) string containing the unit for the values desired.
        @return a list of complex values representing the frequency content.
        @remark
        Valid frequency content units are:\n
        - 'rms' - the root-mean-squared (rms) value.
        - 'dBm' - the values in decibels were 0 dBm corresponds to the voltage needed to deliver
        1 mW to a 50 Ohm load.  It's computed as 20*Log(rms)+13.010.
        - 'dBmPerHz' - the spectral density in dBm/Hz.

        If no unit is specified, the complex frequency content is returned.
        If no valid frequency content units are found, then it defers to the FrequencyDomain base class.

        @see FrequencyDomain.
        """
        if unit=='rms':
            Keven=(self.td.K/2)*2==self.td.K
            A=FrequencyDomain.Values(self,'mag')
            return [A[n]/(1 if (n==0 or ((n==self.m_f.N) and Keven))
                    else math.sqrt(2)) for n in range(len(A))]
        elif unit=='dBm':
            return [-3000. if r < 1e-15 else 20.*math.log10(r)-self.LogRP10
                        for r in self.Values('rms')]
        elif unit=='dBmPerHz':
            Keven=(self.td.K/2)*2==self.td.K
            Deltaf=self.m_f.Fe/self.m_f.N
            adder=-10*math.log10(Deltaf)
            dBm=self.Values('dBm')
            return [dBm[n]+adder+
                    (self.dB3 if (n==0 or ((n==self.m_f.N) and Keven))
                    else 0) for n in range(len(dBm))]
        else: return FrequencyDomain.Values(self,unit)
    def Waveform(self,td=None):
        """Computes the time-domain waveform using IDFT methods
        @param td (optional) instance of class TimeDescriptor declaring the time descriptor of the waveform to produce.
        @return wf instance of class Waveform corresponding to the frequency content.
        @note
        If td is None then the time descriptor corresponding to the frequency descriptor is used.\n
        The waveform produced is essentially the inverse process of class initialization.\n
        @see WaveformFromDefinition()
        """
        Keven=(self.td.K//2)*2==self.td.K
        X=self.Values()
        X=[X[n]*self.td.K*\
            (1. if (n==0 or ((n==self.m_f.N) and Keven)) else 0.5)*\
            cmath.exp(1j*2.*math.pi*self.m_f[n]*self.td.H)
            for n in range(self.m_f.N+1)]
        if Keven:
            X2=[X[self.m_f.N-n].conjugate() for n in range(1,self.m_f.N)]
        else:
            X2=[X[self.m_f.N-n+1].conjugate() for n in range(1,self.m_f.N+1)]
        X.extend(X2)
        x=[xk.real for xk in fft.ifft(X).tolist()]
        wf=Waveform(self.td,x)
        if not td is None:
            wf=wf.Adapt(td)
        return wf
    def WaveformFromDefinition(self,td=None):
        """Computes the time-domain waveform using sums of cosines
        @param td instance of class TimeDescriptor declaring the time descriptor of the waveform to produce.
        @return wf instance of class Waveform corresponding to the frequency content.
        @note
        If td is None then the time descriptor corresponding to the frequency descriptor is used.\n
        The waveform produced is essentially the inverse process of __init__().\n
        This function should produce the exact same result as the Waveform() method, and is slow, but clearly
        written out to see how the waveform is produced by summing sinusoids.  It used to essentially document
        the class.\n
        @see Waveform().
        """
        absX=self.Values('mag')
        theta=self.Values('deg')
        wf=Waveform(self.td)
        for n in range(self.m_f.N+1):
            wf=wf+SineWaveform(self.td,Frequency=self.m_f[n],
                Amplitude=absX[n],Phase=theta[n]+90)
        if not td is None:
            wf=wf.Adapt(td)
        return wf
