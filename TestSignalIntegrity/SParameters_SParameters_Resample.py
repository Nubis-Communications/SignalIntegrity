class SParameters(SParameterManipulation):
...
    def Resample(self,fl):
        if self.m_d is None:
            self.m_f=fl
            copy.deepcopy(self)
        fl=FrequencyList(fl)
        f=FrequencyList(self.f()); f.CheckEvenlySpaced()
        SR=[empty((self.m_P,self.m_P)).tolist() for n in range(fl.N+1)]
        for o in range(self.m_P):
            for i in range(self.m_P):
                res = FrequencyResponse(f,self.Response(o+1,i+1)).Resample(fl)
                for n in range(len(fl)):
                    SR[n][o][i]=res[n]
        return SParameters(fl,SR,self.m_Z0)
...
