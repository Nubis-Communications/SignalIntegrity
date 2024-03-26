class FrequencyResponse(FrequencyDomain):
    def ResampleCZT(self,fdp,speedy=True):
        fd=self.FrequencyList()
        evenlySpaced = fd.CheckEvenlySpaced() and fdp.CheckEvenlySpaced()
        if not evenlySpaced: return self._SplineResample(fdp)
        ir=self.ImpulseResponse()
        TD=ir._FractionalDelayTime()
        Ni=int(min(math.floor(fd.Fe*fdp.N/fdp.Fe),fdp.N))
        Fei=Ni*fdp.Fe/fdp.N
        return FrequencyResponse(EvenlySpacedFrequencyList(Fei,Ni),
            CZT(ir.DelayBy(-TD).Values(),ir.td.Fs,0,Fei,Ni,speedy)).\
            _Pad(fdp.N)._DelayBy(-fd.N/2./fd.Fe+TD)
...
