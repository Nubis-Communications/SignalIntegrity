class FrequencyContent(FrequencyDomain):
    def __init__(self,wf,fd=None):
        td=wf.td
        if fd is None:
            X=fft.fft(wf.Values())
            K=int(td.K)
            Keven = DFTUtilities.Keven(td.K)
            fd=td.FrequencyList()
        else:
            K=fd.N*2
            Keven=True
            X=CZT(wf.Values(),td.Fs,0,fd.Fe,fd.N,True)
            td=TimeDescriptor(td.H,fd.N*2,fd.Fe*2.)
        scale=np.full(fd.N+1,2.); scale[0]=1.
        if Keven: scale[fd.N]=1.
        freqs=np.asarray(fd.Frequencies())[:fd.N+1]
        content=np.asarray(X)[:fd.N+1]/K*scale*np.exp(-1j*2.*math.pi*freqs*td.H)
        FrequencyDomain.__init__(self,fd,content)
        self.td=td
    def Values(self,unit=None):
        if unit=='rms':
            A=np.asarray(FrequencyDomain.Values(self,'mag'))
            divisor=np.full(len(A),math.sqrt(2)); divisor[0]=1.
            if DFTUtilities.Keven(self.td.K): divisor[self.m_f.N]=1.
            return (A/divisor).tolist()
        elif unit=='dBm':
            r=np.asarray(self.Values('rms')); mask=r>=1e-15
            result=np.full(len(r),-3000.)
            result[mask]=20.*np.log10(r[mask])-self.LogRP10
            return result.tolist()
        elif unit=='dBmPerHz':
            adder=-10*math.log10(self.m_f.Fe/self.m_f.N)
            result=np.asarray(self.Values('dBm'))+adder
            result[0]+=self.dB3
            if DFTUtilities.Keven(self.td.K): result[self.m_f.N]+=self.dB3
            return result.tolist()
        else: return FrequencyDomain.Values(self,unit)
...
    def Waveform(self,td=None):
        Keven = DFTUtilities.Keven(self.td.K)
        N=self.m_f.N
        scale=np.full(N+1,0.5); scale[0]=1.
        if Keven: scale[N]=1.
        freqs=np.asarray(self.m_f.Frequencies())[:N+1]
        X=np.asarray(self.Values())*self.td.K*scale*\
            np.exp(1j*2.*math.pi*freqs*self.td.H)
        if Keven:
            X2=np.conjugate(X[N-1:0:-1])
        else:
            X2=np.conjugate(X[N:0:-1])
        x=fft.ifft(np.concatenate([X,X2])).real
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
