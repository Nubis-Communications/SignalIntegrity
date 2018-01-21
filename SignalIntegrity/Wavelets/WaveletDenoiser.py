'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
from Wavelets import WaveletDaubechies4
from SignalIntegrity.TimeDomain.Waveform.Waveform import Waveform
from SignalIntegrity.TimeDomain.Filters.WaveformTrimmer import WaveformTrimmer

import math,cmath
from numpy import std,log2

class WaveletDenoiser(object):
    @staticmethod
    def DenoisedWaveform(wf,pct=30.,mult=5.,isDerivative=True):
        w=WaveletDaubechies4()
        Ki=wf.TimeDescriptor().K
        Kf=int(pow(2,math.ceil(log2(wf.TimeDescriptor().K))))
        PadLeft=Kf-Ki
        pct=pct*Ki/Kf
        pwf=wf*WaveformTrimmer(-PadLeft,0)
        X=w.DWT(pwf.Values())
        T=WaveletDenoiser.DerivativeThresholdCalc(X,w.h,pct,isDerivative)
        # pragma: silent exclude
#         import matplotlib.pyplot as plt
#         plt.clf()
#         plt.title('denoising')
#         plt.loglog([k for k in range(len(X))],[abs(x) for x in X],label='dwt')
#         plt.loglog([k for k in range(len(X))],[t*mult for t in T],label='threshold')
#         plt.xlabel('samples')
#         plt.ylabel('amplitude')
#         plt.legend(loc='upper right')
#         plt.grid(True)
#         plt.show()
        # pragma: include
        dwf =  Waveform(pwf.TimeDescriptor(),w.IDWT([0 if abs(x) < t*mult else x for (x,t) in zip(X,T)]))
        dwf=dwf*WaveformTrimmer(PadLeft,0)
        return dwf
    @staticmethod
    def DerivativeThresholdCalc(X,h,pct=30.,isDerivative=True):
        L=len(h)
        K=len(X)
        N=K/2
        B=int(log2(K)-log2(L))+1
        if isDerivative:
            E=[math.sqrt(2.*(1-math.cos(math.pi*n/N))) for n in range(N+1)]
            TS=WaveletDenoiser.DWTNoiseShapeCalc(E,h)
        else:
            TS=[1 for n in range(N+1)]
        P=int(math.floor(pct/100.*K/2.))
        sigmaw=std(X[K-P:K])
        sigma=sigmaw*math.sqrt(N)/TS[B-1]
        th=[sigma/math.sqrt(N) for k in range(K)]
        for k in range(K):
            # warning - seems to depend on L a power of 2
            b=int(math.floor(log2(max(L/2,k)))-log2(L/2))
            th[k]=th[k]*TS[b]
        return th
    @staticmethod
    def DWTNoiseShapeCalc(E,h):
        L=len(h)
        N=len(E)-1
        B=int(log2(N)-log2(L)+2)
        S=[0 for _ in range(B)]
        for i in range(B-1):
            accn=0.
            for n in range(N+1):
                acc=0.
                for l in range(L):
                    acc=acc+pow(-1,l)*h[L-1-l]*cmath.exp(-1j*math.pi*n*l/N)
                accn=accn+pow(abs(E[n])*abs(acc),2)
            S[B-1-i]=math.sqrt(accn)
            for n in range(N/2+1):
                accl=0
                accr=0
                for l in range(L):
                    accl=accl+h[l]*cmath.exp(-1j*math.pi*n*l/N)
                    accr=accr+h[l]*cmath.exp(-1j*math.pi*(N-n)*l/N)
                E[n]=math.sqrt(pow(abs(E[n])*abs(accl),2.)+pow(abs(E[N-n])*abs(accr),2.))
            N=N/2
        acc=0
        for n in range(N+1):
            acc=acc+pow(abs(E[n]),2)
        S[0]=math.sqrt(acc)
        return S
