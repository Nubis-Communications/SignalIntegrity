class TransferMatrices(list,CallBacker):
    def __init__(self,f,d):
        self.f=FrequencyList(f)
        list.__init__(self,d)
        CallBacker.__init__(self)
        self.Inputs=len(d[0][0])
        self.Outputs=len(d[0])
        self.fr=None
        self.ir=None
        self.td=None
...
    def FrequencyResponse(self,o,i):
        if not self.cacheResponses or self.fr == None:
            return FrequencyResponse(self.f,[Matrix[o-1][i-1]
                                             for Matrix in self])
        else:
            return copy.deepcopy(self.fr[o-1][i-1])
    def FrequencyResponses(self):
        if not self.cacheResponses or self.fr==None:
            fr = [[None for s in range(self.Inputs)] for o in range(self.Outputs)]
            for o in range(self.Outputs):
                for s in range(self.Inputs):
                    fr[o][s] = self.FrequencyResponse(o+1,s+1)
                    if not self.CallBack((o*self.Inputs+s)/
                                         (self.Inputs*self.Outputs)*100.0):
                        return None
            if not self.cacheResponses:
                return fr
            self.fr = fr
        return copy.deepcopy(self.fr)
    def ImpulseResponses(self,td=None,time_before_0=None):
        fr = self.FrequencyResponses()
        if td is None or isinstance(td,float) or isinstance(td,int):
            td = [td for _ in range(self.Inputs)]
        if fr == None:
            return None

        if self.cacheResponses and self.td == td and self.ir != None:
            return self.ir

        ir = [[None for s in range(self.Inputs)] for o in range(self.Outputs)]

        for o in range(self.Outputs):
            for s in range(self.Inputs):
                ir[o][s] = fr[o][s].ImpulseResponse(td[s],time_before_0=time_before_0)
                if not self.CallBack((o*self.Inputs+s)/
                                     (self.Inputs*self.Outputs)*100.0):
                    return None

        if not self.cacheResponses:
            return ir

        self.ir = ir
        self.td = td
        return copy.deepcopy(self.ir)
    def Resample(self,fdp):
        fr = self.FrequencyResponses()
        fr = [[fr[o][s].Resample(fdp)
            for s in range(self.Inputs)]
               for o in range(self.Outputs)]
        d = [[[fr[o][s][n]
               for s in range(self.Inputs)]
                    for o in range(self.Outputs)]
                        for n in range(len(fdp))]
        return TransferMatrices(fdp,d)
