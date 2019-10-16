class FrequencyResponse(FrequencyDomain):
    def Resample(self,fdp):
        Result=FrequencyResponse(self.FrequencyList(),self.Values())
        fd=Result.FrequencyList()
        evenlySpaced = fd.CheckEvenlySpaced() and fdp.CheckEvenlySpaced()
        if not evenlySpaced: return Result._SplineResample(fdp)
        R=Rat(fd.Fe/fdp.Fe*fdp.N); ND1=R[0]; D2=R[1]
        if ND1 < fd.N: R=Rat(fd.Fe/fdp.Fe*fdp.N/fd.N); ND1=R[0]*fd.N; D2=R[1]
        if  ND1 > 50000: return Result.ResampleCZT(fdp)
        if ND1 == fd.N: fr=Result
        else: fr=Result.ImpulseResponse()._Pad(2*ND1).FrequencyResponse(None,False)
        if D2*fdp.N != ND1: fr=fr._Pad(D2*fdp.N)
        if D2==1: return fr
        else: return fr._Decimate(D2)
...
