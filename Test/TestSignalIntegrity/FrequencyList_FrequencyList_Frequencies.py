class FrequencyList(list):
...
    def SetEvenlySpaced(self,Fe,N):
        self.Fe=Fe
        self.N=int(N)
        list.__init__(self,[Fe/N*n for n in range(self.N+1)])
        self.m_EvenlySpaced=True
        return self
    def SetList(self,fl):
        list.__init__(self,fl)
        self.N=len(fl)-1
        self.Fe=fl[-1]
        self.m_EvenlySpaced=False
        return self
    def EvenlySpaced(self): return self.m_EvenlySpaced
    def Frequencies(self,unit=None):
        if unit == None: return list(self)
        elif isinstance(unit,float): return (self/unit).Frequencies()
        elif unit == 'GHz': return (self/1.e9).Frequencies()
        elif unit == 'MHz': return (self/1.e6).Frequencies()
        elif unit == 'kHz': return (self/1.e3).Frequencies()
    def CheckEvenlySpaced(self,epsilon=0.01):
        if self.m_EvenlySpaced: return True
        for n in range(self.N+1):
            try:
                if abs(self[n]-self.Fe/self.N*n) > epsilon:
                    self.m_EvenlySpaced=False
                    return False
            except:
                return False
        self.SetEvenlySpaced(self.Fe,self.N)
        return True
    def __div__(self,d):
        return self.__truediv__(d)
    def __truediv__(self,d):
        if self.EvenlySpaced(): return EvenlySpacedFrequencyList(self.Fe/d,self.N)
        else: return GenericFrequencyList([v/d for v in self])
    def __mul__(self,d):
        if self.EvenlySpaced(): return EvenlySpacedFrequencyList(self.Fe*d,self.N)
        else: return GenericFrequencyList([v*d for v in self])
    def TimeDescriptor(self,Keven=True):
        N=self.N
        K=2*N
        if not Keven: K=K+1
        Fs=self.Fe*K/N
        return TimeDescriptor(-K/2./Fs,K,Fs)
...
