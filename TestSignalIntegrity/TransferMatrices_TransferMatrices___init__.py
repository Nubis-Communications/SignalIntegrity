class TransferMatrices(list):
    def __init__(self,f,d):
        self.f=FrequencyList(f)
        list.__init__(self,d)
        self.Inputs=len(d[0][0])
        self.Outputs=len(d[0])
...
    def FrequencyResponse(self,o,i):
        return FrequencyResponse(self.f,[Matrix[o-1][i-1]
            for Matrix in self])
    def FrequencyResponses(self):
        return [[self.FrequencyResponse(o+1,s+1)
            for s in range(self.Inputs)] for o in range(self.Outputs)]
    def ImpulseResponses(self,td=None):
        fr = self.FrequencyResponses()
        if td is None or isinstance(td,float) or isinstance(td,int):
            td = [td for m in range(len(fr[0]))]
        return [[fro[m].ImpulseResponse(td[m]) for m in range(len(fro))]
            for fro in fr]
