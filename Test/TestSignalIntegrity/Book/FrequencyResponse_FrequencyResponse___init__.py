class FrequencyResponse(FrequencyDomain):
    def __init__(self,f=None,resp=None):
        FrequencyDomain.__init__(self,f,resp)
    def Response(self,unit=None):
        return self.Values(unit)
...
