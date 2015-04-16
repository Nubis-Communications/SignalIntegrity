from numpy import fft
import cmath
import math
from SignalIntegrity.SParameters import SParameters
from numpy import empty

def CZT(x,Fs,fs,fe,M,highSpeed=True):
    M=int(M)
    K=len(x)
    fs=float(fs)
    Fs=float(Fs)
    fe=float(fe)
    theta0=fs/Fs
    phi0=(fe-fs)/Fs*1./M
    A0=1.
    W0=1.
    A=A0*cmath.exp(1j*2.*math.pi*theta0)
    W=W0*cmath.exp(1j*2.*math.pi*phi0)
    if highSpeed:
        L=pow(2,int(math.ceil(math.log(float(M+K),2.))))*2
        v=[0 for l in range(L)]
        for k in range(M+1):
            v[k]=pow(W,float(k*k)/2.)
        for k in range(M+1,L-K+1):
            v[k]=0.
        for k in range(L-K+1,L):
            v[k]=pow(W,(L-k)*(L-k)/2.)
        V=fft.fft(v)
        y = [0 for l in range(L)]
        for k in range(K):
            y[k]=x[k]*pow(A,-k)*pow(W,-(k*k)/2.)
        for k in range(K,L):
            y[k]=0
        Y=fft.fft(y)
        P=[Y[l]*V[l] for l in range(L)]
        P=fft.ifft(P)
        X = [P[m]/v[m] for m in range(M+1)]
    else:
        X=[]
        for m in range(M+1):
            Xm=0.
            for k in range(K):
                Xm=Xm+x[k]*pow(A*pow(W,m),-k)
            X.append(Xm)
    return X

def CZTResample(S,Fep,Np,imposeRealness=False):
    Fsp=Fep*2.
    N=len(S)-1
    Fs=S.f()[N]*2
    P=S.m_P
    fp=[float(np)/Np*Fsp/2. for np in range(Np+1)]
    SppR=[empty((P,P)).tolist() for np in range(Np+1)]
    for r in range(P):
        for c in range(P):
            X=S.Response(r+1,c+1)
            if imposeRealness:
                X[0]=X[0].real
                X[N]=X[N].real
            X2 = [X[N-nn].conjugate() for nn in range(1,N)]
            X=X+X2
            K=2*N
            x=fft.ifft(X)
            SD=int(K/2)
            TD=SD/Fs
            xd = [x[K+k-SD] if k-SD < 0 else x[k-SD] for k in range(K)]
            if imposeRealness: xd = [ele.real for ele in xd]
            SppPrime=CZT(xd,Fs,0.,Fep,Np,True)
            for np in range(Np+1):
                if fp[np] <= S.f()[N]:
                    SppPrime[np]=SppPrime[np]*cmath.exp(1j*2.*math.pi*fp[np]*TD)
                    SppR[np][r][c]=SppPrime[np]
                else:
                    SppR[np][r][c]=0.001
    return SParameters(fp,SppR,S.m_Z0)
