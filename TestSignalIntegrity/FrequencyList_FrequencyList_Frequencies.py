class FrequencyList(object):
    def __init__(self,f=None):
        if isinstance(f,FrequencyList):
            self.List=f.List
            self.N=f.N
            self.Fe=f.Fe
            self.m_EvenlySpaced=f.m_EvenlySpaced
        elif isinstance(f,list): self.SetList(f)
    def SetEvenlySpaced(self,Fe,N):
        self.Fe=Fe
        self.N=N
        self.List=[Fe/N*n for n in range(N+1)]
        self.m_EvenlySpaced=True
        return self
    def SetList(self,fl):
        self.List=fl
        self.N=len(fl)-1
        self.Fe=fl[-1]
        self.m_EvenlySpaced=False
        return self
    def EvenlySpaced(self):
        return self.m_EvenlySpaced
    def Frequencies(self,unit=None):
        if unit == None:
            return self.List
        elif isinstance(unit,float):
            return (self/unit).Frequencies()
        elif unit == 'GHz':
            return (self/1.e9).Frequencies()
        elif unit == 'MHz':
            return (self/1.e6).Frequencies()
        elif unit == 'KHz':
            return (self/1.e3).Frequencies()
    def CheckEvenlySpaced(self,epsilon=0.01):
        if self.m_EvenlySpaced:
            return True
        for n in range(self.N+1):
            if abs(self.List[n]-self.Fe/self.N*n) > epsilon:
                self.m_EvenlySpaced=False
                return False
        self.SetEvenlySpaced(self.Fe,self.N)
        return True
    def __getitem__(self,item): return self.List[item]
    def __len__(self): return len(self.List)
    def __div__(self,d):
        if self.EvenlySpaced():
            return EvenlySpacedFrequencyList(self.Fe/d,self.N)
        else:
            return GenericFrequencyList([v/d for v in self.List])
    def TimeDescriptor(self):
        N=self.N
        Fs=2.*self.Fe
        K=2*N
        return TimeDescriptor(-K/2./Fs,K,Fs)
...
