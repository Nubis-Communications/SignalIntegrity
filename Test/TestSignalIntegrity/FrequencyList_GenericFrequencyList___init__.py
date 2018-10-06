class GenericFrequencyList(FrequencyList):
    def __init__(self,fl):
        FrequencyList.__init__(self)
        self.SetList(fl)