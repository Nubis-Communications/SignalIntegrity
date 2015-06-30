class FrequencyResponse(object):
...
    def _DelayBy(self,TD):
        fd=self.FrequencyList()
        return FrequencyResponse(fd,
            [self.Response()[n]*cmath.exp(-1j*2.*math.pi*fd[n]*TD) for n in range(fd.N+1)])
...
