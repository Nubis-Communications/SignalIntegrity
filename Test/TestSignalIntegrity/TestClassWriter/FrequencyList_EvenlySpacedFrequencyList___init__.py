class EvenlySpacedFrequencyList(FrequencyList):
    def __init__(self,Fe,Np):
        FrequencyList.__init__(self)
        self.SetEvenlySpaced(Fe,Np)

