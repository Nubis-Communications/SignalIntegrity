class FrequencyResponse(object):
...
    def Resample(self,fd):
        evenlySpaced = self.FrequencyList().CheckEvenlySpaced()
        if not evenlySpaced:
            newfd = fd
            oldfd = self.FrequencyList()
            Poly=Spline(oldfd,self.Response())
            newresp=[Poly.Evaluate(f) if f <= oldfd[-1] else 0.0001 for f in newfd]
            newfr=FrequencyResponse(newfd,newresp)
            return newfr
        P=2*min(Rat(self.FrequencyList().Fe/fd.Fe*fd.N)[0],100000)
        K=self.FrequencyList().N*2
        D=K/P # decimation factor for frequency response equivalent to padding
        # pad the impulse response to put the new frequencies on the grid
        if P==K:
            # the pad amount is the same as the number of points in the impulse
            # response.  The frequencies are already on the grid
            fr=self
        elif P*D == K:
            # desired number of points is an integer multiple of the pad amount
            # the frequency response can be simply decimated by this multiple
            fr=self._Decimate(D)
        else:
            # the pad amount is not the same as the original impulse response and
            # the original impulse response length is not an integer multiple of the
            # pad amount.  Therefore pad the impulse response and recompute the
            # frequency response
            fr=self.ImpulseResponse()._Pad(P).FrequencyResponse(None,False)
        # often, after padding the impulse response to get things on the right
        # frequency scale, the frequency response is just right
        if fd.N == fr.FrequencyList().N and fd.Fe == fr.FrequencyList().Fe:
            return fr
        # The frequency response in fr is now what gets resampled.  It is probably
        # on the desired frequency grid (it might not be if the pad amount got limited
        # above.  If not, it's at the finest spacing possible.
        fr=fr._Pad(P=int(math.ceil(fd.Fe/fr.FrequencyList().Fe*fr.FrequencyList().N)))
        # the padded response might be right
        if fd.N == fr.FrequencyList().N and fd.Fe == fr.FrequencyList().Fe:
            return fr
        # otherwise, if the end frequency of the padded response is the desired end
        # frequency and if the number of points is an integer multiple of the desired
        # number of points, then just decimate the padded response
        if fr.FrequencyList().Fe == fd.Fe and fr.FrequencyList().N/fd.N*fd.N ==\
                fr.FrequencyList().N:
            return fr._Decimate(fr.FrequencyList().N/fd.N)
        # this is the last resort.  The padded frequency response is now resampled
        # using the CZT on the impulse response
        ir=fr.ImpulseResponse()
        Ts=1./ir.TimeDescriptor().Fs
        H=ir.TimeDescriptor().H
        TD=-Ts*(-H/Ts-math.floor(-H/Ts+0.5))
        ir=ir.DelayBy(-TD)
        X=CZT(ir.Values(),ir.TimeDescriptor().Fs,0,fd.Fe,fd.N,highSpeed=True)
        return FrequencyResponse(fd,X)._DelayBy(-ir.TimeDescriptor().N/2./
                                                ir.TimeDescriptor().Fs+TD)
...
