class FrequencyContent(FrequencyDomain):
    def __init__(self,wf,fd=None):
        td=wf.td
        if fd is None:
            X=fft.fft(wf.Values())
            K=int(td.K)
            Keven=(K//2)*2 == K
            fd=td.FrequencyList()
        else:
            K=fd.N*2
            Keven=True
            X=CZT(wf.Values(),td.Fs,0,fd.Fe,fd.N,True)
            td=TimeDescriptor(td.H,fd.N*2,fd.Fe*2.)
        FrequencyDomain.__init__(self,fd,[X[n]/K*\
            (1. if (n==0 or ((n==fd.N) and Keven)) else 2.)*\
            cmath.exp(-1j*2.*math.pi*fd[n]*td.H) for n in range(fd.N+1)])
        self.td=td
    def Values(self,unit=None):
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
        absX=self.Values('mag')
        theta=self.Values('deg')
        wf=Waveform(self.td)
        for n in range(self.m_f.N+1):
            wf=wf+SineWaveform(self.td,Frequency=self.m_f[n],
                Amplitude=absX[n],Phase=theta[n]+90)
        if not td is None:
            wf=wf.Adapt(td)
        return wf
