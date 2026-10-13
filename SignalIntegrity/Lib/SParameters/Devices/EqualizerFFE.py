"""EqualizerFFE"""

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

import cmath
import numpy as np

class FFE(SParameters):
    """Linear feed-forward equalizer"""
    def __init__(self,f,Td,taps,numPreCursorTaps,Z0=50.):
        """Constructor
        @param f list of float frequencies
        @param Td float time delay of each tap
        @param taps list of float values of the taps
        @param numPreCursorTaps integer number of precursor taps
        @param Z0 float (optional, defaults to 50) reference impedance
        @remark Usually Td is the reciprocal of the baud rate or sometimes, half the reciprocal.
        """
        self.Td=Td
        self.taps=taps
        self.PC=numPreCursorTaps
        SParameters.__init__(self,f,None,Z0)
    def _Evaluate(self,f):
        """Evaluate FFE
        @param f float frequency
        @return FFE evaluated at f
        """
        K=len(self.taps)
        return sum([self.taps[k]*cmath.exp(1j*2.*cmath.pi*f*-(k-self.PC)*self.Td) for k in range(K)])
    def _ResponseVector(self):
        """Frequency response evaluated at all frequencies.

        The FFE frequency response is the discrete-time Fourier transform of the
        tap sequence.  Evaluating it as a scalar sum over the taps at every
        frequency is O(frequencies x taps), which becomes very slow when the tap
        count is large (e.g. long-risetime risetime filters).  This computes the
        whole response at once: an FFT-based evaluation (with tap folding) when the
        frequency list is evenly spaced from DC and aligns with the tap delay, and
        a vectorized (chunked) evaluation otherwise.  The result is cached.
        @return numpy array of the response at each frequency.
        """
        try:
            return self._responseVector
        except AttributeError:
            pass
        taps=np.asarray(self.taps,dtype=complex)
        K=len(taps)
        f=np.asarray(self.m_f,dtype=float)
        Np=len(f); Td=self.Td; PC=self.PC
        H=None
        if Np>=2 and K>0 and Td!=0:
            df=f[1]-f[0]
            if df>0 and np.allclose(np.diff(f),df,rtol=1e-9,atol=0.0) and abs(f[0])<=1e-9*df:
                Mfloat=1.0/(df*Td)
                M=int(round(Mfloat))
                if M>=1 and abs(Mfloat-M)<=1e-6*M:
                    # H[n]=exp(j2*pi*n*PC/M)*sum_k taps[k]*exp(-j2*pi*n*k/M); the inner
                    # sum is the length-M DFT of the taps folded modulo M.
                    g=np.zeros(M,dtype=complex)
                    np.add.at(g,np.arange(K)%M,taps)
                    G=np.fft.fft(g)
                    n=np.arange(Np)
                    H=np.exp(1j*2.*np.pi*n*PC/M)*G[n%M]
        if H is None:
            # general vectorized fallback, chunked over frequency to bound memory
            kv=np.arange(K)-PC
            base=-1j*2.*np.pi*Td
            H=np.empty(Np,dtype=complex)
            chunk=max(1,4000000//max(K,1))
            for s in range(0,Np,chunk):
                e=min(s+chunk,Np)
                H[s:e]=np.exp(base*np.outer(f[s:e],kv)).dot(taps)
        self._responseVector=H
        return H
    def __getitem__(self,n):
        return [[1.,0],[2.*complex(self._ResponseVector()[n]),-1.]]
