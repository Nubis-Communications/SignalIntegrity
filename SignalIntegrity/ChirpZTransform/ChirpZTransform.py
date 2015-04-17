from numpy import fft
import cmath
import math
from numpy import empty

def CZT(x,Fs,fs,fe,M,highSpeed=True):
    M=int(M); K=len(x); fs=float(fs); Fs=float(Fs); fe=float(fe)
    theta0=fs/Fs; phi0=(fe-fs)/Fs*1./M; A0=1.; W0=1.
    A=A0*cmath.exp(1j*2.*math.pi*theta0)
    W=W0*cmath.exp(1j*2.*math.pi*phi0)
    if highSpeed:
        L=pow(2,int(math.ceil(math.log(float(M+K),2.))))*2
        v=[0 for l in range(L)]
        for k in range(M+1): v[k]=pow(W,float(k*k)/2.)
        for k in range(M+1,L-K+1): v[k]=0.
        for k in range(L-K+1,L): v[k]=pow(W,(L-k)*(L-k)/2.)
        V=fft.fft(v)
        y = [0 for l in range(L)]
        for k in range(K): y[k]=x[k]*pow(A,-k)*pow(W,-(k*k)/2.)
        for k in range(K,L): y[k]=0
        Y=fft.fft(y)
        P=[Y[l]*V[l] for l in range(L)]
        P=fft.ifft(P)
        X = [P[m]/v[m] for m in range(M+1)]
    else:
        X=[]
        for m in range(M+1):
            Xm=0.
            for k in range(K): Xm=Xm+x[k]*pow(A*pow(W,m),-k)
            X.append(Xm)
    return X