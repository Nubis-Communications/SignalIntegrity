'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
import math
import cmath

from numpy import fft

from SignalIntegrity.PySIException import PySIExceptionWaveform
from SignalIntegrity.FrequencyDomain.FrequencyDomain import FrequencyDomain
from SignalIntegrity.Splines import Spline
from SignalIntegrity.TimeDomain.Waveform.Waveform import Waveform
from SignalIntegrity.TimeDomain.Waveform.SineWaveform import SineWaveform
from SignalIntegrity.ChirpZTransform.ChirpZTransform import CZT
from SignalIntegrity.TimeDomain.Waveform.TimeDescriptor import TimeDescriptor

class FrequencyContent(FrequencyDomain):
    def __init__(self,wf,fd=None):
        td=wf.TimeDescriptor()
        if fd is None:
            X=fft.fft(wf.Values())
            K=int(td.N)
            Keven=(K/2)*2 == K
            fd=td.FrequencyList()
        else:
            # pragma: silent exclude
            if not fd.EvenlySpaced():
                raise PySIExceptionWaveform('cannot generate frequency content')
            # pragma: include
            K=fd.N*2
            Keven=True
            X=CZT(wf.Values(),td.Fs,0,fd.Fe,fd.N,True)
            td=TimeDescriptor(td.H,fd.N*2,fd.Fe/2.)
        FrequencyDomain.__init__(self,fd,[X[n]/K*\
            (1. if (n==0 or ((n==fd.N) and Keven)) else 2.)*\
            cmath.exp(-1j*2.*math.pi*fd[n]*td.H) for n in range(fd.N+1)])
        self.td=td
    def Content(self,unit=None):
        return self.Values(unit)
    def Waveform(self,td=None):
        K=self.td.N
        Keven=(K/2)*2==K
        X=self.Values()
        X=[X[n]*K*\
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
        absX=self.Values('mag')
        theta=self.Values('deg')
        wf=Waveform(self.td)
        for n in range(self.m_f.N+1):
            wf=wf+SineWaveform(self.td,Frequency=self.m_f[n],
                Amplitude=absX[n],Phase=theta[n]+90)
        if not td is None:
            wf=wf.Adapt(td)
        return wf
    def PSD(self):
        K=self.td.N
        Keven=(K/2)*2==K
        X=self.Values('dB')
        Deltaf=self.m_f.Fe/self.td.N
        adder=13.010-10*math.log10(Deltaf)
        X=[X[n]+adder+(6. if (n==0 or ((n==self.m_f.N) and Keven)) else 0.0)
           for n in range(self.m_f.N+1)]
        return X
