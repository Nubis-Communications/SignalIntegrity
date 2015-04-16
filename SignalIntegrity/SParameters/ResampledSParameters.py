from SignalIntegrity.SParameters.SParameters import SParameters
from SignalIntegrity.Splines import Spline
from SignalIntegrity.ChirpZTransform import CZT

from numpy import fft
import cmath
import math
from numpy import empty

class ResampledSParameters(SParameters):
    def __init__(self,S,Fep,Np,**args):
        method = args['method'] if 'method' in args else 'spline'
        highSpeed = args['speed']=='high' if 'speed' in args else True
        imposeRealness = args['enforceReal']=='true' if 'enforceReal' in args else False
        Fsp=Fep*2.
        N=len(S)-1
        Fs=S.f()[N]*2
        P=S.m_P
        K=2*N
        SD=int(K/2)
        TD=SD/Fs
        fp = [Fep/Np*np for np in range(Np+1)]
        SppR=[empty((P,P)).tolist() for np in range(Np+1)]
        for r in range(P):
            for c in range(P):
                X=S.Response(r+1,c+1)
                if method == 'spline':
                    Poly=Spline(S.f(),X)
                    SppPrime=[Poly.Evaluate(f) if f <= S.f()[N] else 0.001 for f in fp]
                elif method == 'czt':
                    if imposeRealness:
                        X[0]=X[0].real
                        X[N]=X[N].real
                    X2 = [X[N-nn].conjugate() for nn in range(1,N)]
                    X=X+X2
                    x=fft.ifft(X)
                    xd = [x[K+k-SD] if k-SD < 0 else x[k-SD] for k in range(K)]
                    if imposeRealness: xd = [ele.real for ele in xd]
                    SppPrime=CZT(xd,Fs,0.,Fep,Np,highSpeed)
                    SppPrime = [SppPrime[np]*cmath.exp(1j*2.*math.pi*fp[np]*TD) if fp[np] <= S.f()[N] else 0.001 for np in range(Np+1)]
                for np in range(Np+1):
                    SppR[np][r][c]=SppPrime[np]
        SParameters.__init__(self,fp,SppR,S.m_Z0)