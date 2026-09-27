class FrequencyResponse(FrequencyDomain):
    def _DelayBy(self,TD):
        fd=self.FrequencyList()
        return FrequencyResponse(fd,
        [self[n]*cmath.exp(-1j*2.*math.pi*fd[n]*TD)
            for n in range(fd.N+1)])
...
    def _FractionalDelayTime(self):
        ir = self.ImpulseResponse(None,adjustDelay=False)
        idx = ir.Values('abs').index(max(ir.Values('abs')))
        TD = ir.td[idx] # the time of the main peak
        # calculate the frequency response with this delay taken out
        # the fractional delay is based on the minimum adjustment to the phase of
        # the last point to make that point real
        theta = self._DelayBy(-TD).Response('rad')[self.FrequencyList().N]
        # do not make this adjustment if the phase is of a tiny magnitude!
        if self.Response('dB')[self.FrequencyList().N]<-90: theta=0.
        if theta < -math.pi/2.: theta=-(math.pi+theta)
        elif theta > math.pi/2.: theta = math.pi-theta
        else: theta = -theta
        # calculate the fractional delay
        TD=theta/2./math.pi/self.FrequencyList()[-1]
        return TD
...
