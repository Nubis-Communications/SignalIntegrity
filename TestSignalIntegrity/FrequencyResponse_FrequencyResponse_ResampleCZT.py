class FrequencyResponse(object):
...
    def ResampleCZT(self,fdp):
        fd=self.FrequencyList()
        evenlySpaced = fd.CheckEvenlySpaced() and fdp.CheckEvenlySpaced()
        if not evenlySpaced: return self._SplineResample(fdp)
        ir=self.ImpulseResponse()
        td=ir.TimeDescriptor()
        TD=-(-td.H*td.Fs-math.floor(-td.H*td.Fs+0.5))/td.Fs
        Ni=int(math.floor(fd.Fe*fdp.N/fdp.Fe))
        Fei=Ni*fdp.Fe/fdp.N
        return FrequencyResponse(EvenlySpacedFrequencyList(Fei,Ni),
            CZT(ir.DelayBy(-TD).Values(),td.Fs,0,Fei,Ni)).\
            _Pad(fdp.N)._DelayBy(-fd.N/2./fd.Fe+TD)
...
