class FrequencyList(object):
    def __init__(self,f=None):
        if isinstance(f,FrequencyList):
            self.m_fl=f.m_fl
            self.m_Np=f.m_Np
            self.m_Fe=f.m_Fe
            self.m_EvenlySpaced=f.m_EvenlySpaced
        elif isinstance(f,list): self.SetList(f)
    def SetEvenlySpaced(self,Fe,Np):
        self.m_Fe=Fe
        self.m_Np=Np
        self.m_fl=[Fe/Np*n for n in range(Np+1)]
        self.m_EvenlySpaced=True
        return self
    def SetList(self,fl):
        self.m_fl=fl
        self.m_Np=len(fl)-1
        self.m_Fe=fl[-1]
        self.m_EvenlySpaced=False
        return self
    def EvenlySpaced(self):
        return self.m_EvenlySpaced
    def List(self):
        return self.m_fl
    def CheckEvenlySpaced(self,epsilon=0.001):
        if self.m_EvenlySpaced:
            return True
        for n in range(self.m_Np+1):
            if abs(self.m_fl[n]-self.m_Fe/self.m_Np*n) > epsilon:
                self.m_EvenlySpaced=False
                return False
        self.SetEvenlySpaced(self.m_Fe,self.m_Np)
        return True
    def __getitem__(self,item): return self.m_fl[item]
    def __len__(self): return len(self.m_fl)

class EvenlySpacedFrequencyList(FrequencyList):
    def __init__(self,Fe,Np):
        FrequencyList.__init__(self)
        self.SetEvenlySpaced(Fe,Np)

class GenericFrequencyList(FrequencyList):
    def __init__(self,fl):
        FrequencyList.__init__(self)
        self.SetList(fl)






