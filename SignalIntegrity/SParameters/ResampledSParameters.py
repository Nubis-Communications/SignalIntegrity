from SignalIntegrity.SParameters.SParameters import SParameters
from SignalIntegrity.Splines import Spline
from SignalIntegrity.ChirpZTransform import CZT
from SignalIntegrity.SParameters.FrequencyList import *

from numpy import fft
import cmath
import math
from numpy import empty

class ResampledSParameters(SParameters):
    def __init__(self,S,fl,**args):
        fl=FrequencyList(fl)
        method = args['method'] if 'method' in args else 'spline'
        truncate = args['truncate'] if 'truncate' in args else True
        if method == 'czt' and not S.f().CheckEvenlySpaced():
                method = 'spline'
        highSpeed = args['speed']=='high' if 'speed' in args else True
        imposeRealness = args['enforceReal'] if 'enforceReal' in args else False
        N=len(S)-1
        Fs=S.f()[N]*2
        K=2*N
        SD=int(K/2)
        TD=SD/Fs
        fp = fl.List()
        SppR=[empty((S.m_P,S.m_P)).tolist() for np in range(fl.m_Np+1)]
        for r in range(S.m_P):
            for c in range(S.m_P):
                X=S.Response(r+1,c+1)
                if method == 'spline':
                    Poly=Spline(S.f(),X)
                    SppPrime=[Poly.Evaluate(f)
                        if f <= S.f()[N] or not truncate else 0.0001
                            for f in fp]
                elif method == 'czt':
                    if imposeRealness:
                        X[0]=X[0].real
                        X[N]=X[N].real
                    X2 = [X[N-nn].conjugate() for nn in range(1,N)]
                    X=X+X2
                    x=fft.ifft(X)
                    xd = [x[K+k-SD] if k-SD < 0 else x[k-SD] for k in range(K)]
                    if imposeRealness: xd = [ele.real for ele in xd]
                    SppPrime=CZT(xd,Fs,0.,fl.m_Fe,fl.m_Np,highSpeed)
                    SppPrime = [SppPrime[np]*cmath.exp(1j*2.*math.pi*fp[np]*TD)
                        if fp[np] <= S.f()[N] or not truncate else 0.001
                            for np in range(fl.m_Np+1)]
                for np in range(fl.m_Np+1):
                    SppR[np][r][c]=SppPrime[np]
        SParameters.__init__(self,fp,SppR,S.m_Z0)