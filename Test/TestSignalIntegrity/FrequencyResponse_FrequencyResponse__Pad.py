class FrequencyResponse(FrequencyDomain):
...
    def _Pad(self,P):
        fd=self.FrequencyList()
        if P == fd.N: X=self.Response()
        elif P < fd.N: X=self.Response()[:P+1]
        else: X=self.Response()+[0]*(P-fd.N)
        return FrequencyResponse(EvenlySpacedFrequencyList(P*fd.Fe/fd.N,P),X)
...
