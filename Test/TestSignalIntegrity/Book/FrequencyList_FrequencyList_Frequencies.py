class FrequencyList(object):
...
    def SetEvenlySpaced(self,Fe,N):
        self.Fe=Fe
        self.N=int(N)
        self.values=(Fe/N)*np.arange(self.N+1)
        self.m_EvenlySpaced=True
        return self
    def SetList(self,fl):
        self.values=np.asarray(fl,dtype=float)
        self.N=len(self.values)-1
        self.Fe=self.values[-1]
        self.m_EvenlySpaced=False
        return self
    def EvenlySpaced(self): return self.m_EvenlySpaced
    def Frequencies(self,unit=None):
        if unit == None: return self.values.copy()
        elif isinstance(unit,float): return (self/unit).Frequencies()
        elif unit == 'GHz': return (self/1.e9).Frequencies()
        elif unit == 'MHz': return (self/1.e6).Frequencies()
        elif unit == 'kHz': return (self/1.e3).Frequencies()
    def CheckEvenlySpaced(self,epsilon=0.01):
        if self.m_EvenlySpaced: return True
        if len(self.values) != self.N+1:
            return False
        expected=self.Fe/self.N*np.arange(self.N+1)
        if np.any(np.abs(self.values-expected) > epsilon):
            self.m_EvenlySpaced=False
            return False
        self.SetEvenlySpaced(self.Fe,self.N)
        return True
    def __div__(self,d):
        return self.__truediv__(d)
    def __truediv__(self,d):
        if self.EvenlySpaced(): return EvenlySpacedFrequencyList(self.Fe/d,self.N)
        else: return GenericFrequencyList(self.values/d)
    def __mul__(self,d):
        if self.EvenlySpaced(): return EvenlySpacedFrequencyList(self.Fe*d,self.N)
        else: return GenericFrequencyList(self.values*d)
    def TimeDescriptor(self,Keven=True):
        N=self.N
        K=2*N
        if not Keven: K=K+1
        Fs=self.Fe*K/N
        return TimeDescriptor(-K/2./Fs,K,Fs)
...
