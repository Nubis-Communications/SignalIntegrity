class FrequencyResponse(FrequencyDomain):
    def Resample(self,fdp):
        fd=self.FrequencyList()
        evenlySpaced = fd.CheckEvenlySpaced() and fdp.CheckEvenlySpaced()
        if not evenlySpaced:
            if self.remove_principal_delay:
                # first, remove the principal delay
                Td=self.PrincipalDelay(fd=True)
            else:
                Td=0
            fr=self._DelayBy(-Td)
            frDelayed=fr._SplineResample(fdp)
            fr=frDelayed._DelayBy(Td)
            return fr
        R=Rat(fd.Fe/fdp.Fe*fdp.N); ND1=R[0]; D2=R[1]
        if ND1 < fd.N: R=Rat(fd.Fe/fdp.Fe*fdp.N/fd.N); ND1=R[0]*fd.N; D2=R[1]
        if  ND1 > 50000: return self.ResampleCZT(fdp)
        if ND1 == fd.N: fr=self
        else: fr=self.ImpulseResponse()._Pad(2*ND1).FrequencyResponse(None,False)
        if D2*fdp.N != ND1: fr=fr._Pad(D2*fdp.N)
        if D2==1: return fr
        else: return fr._Decimate(D2)
...
