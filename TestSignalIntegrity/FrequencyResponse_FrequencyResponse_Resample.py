class FrequencyResponse(object):
...
    def Resample(self,fdp):
        fd=self.FrequencyList()
        evenlySpaced = fd.CheckEvenlySpaced() and fdp.CheckEvenlySpaced()
        if not evenlySpaced: return self._SplineResample(fdp)
        P=2*min(Rat(self.FrequencyList().Fe/fdp.Fe*fdp.N/self.FrequencyList().N)[0]*self.FrequencyList().N,100000)
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
        if fdp.N == fr.FrequencyList().N and fdp.Fe == fr.FrequencyList().Fe:
            return fr
        # The frequency response in fr is now what gets resampled.  It is probably
        # on the desired frequency grid (it might not be if the pad amount got limited
        # above.  If not, it's at the finest spacing possible.
        fr=fr._Pad(P=int(math.ceil(fdp.Fe/fr.FrequencyList().Fe*fr.FrequencyList().N)))
        # the padded response might be right
        if fdp.N == fr.FrequencyList().N and fdp.Fe == fr.FrequencyList().Fe:
            return fr
        # otherwise, if the end frequency of the padded response is the desired end
        # frequency and if the number of points is an integer multiple of the desired
        # number of points, then just decimate the padded response
        if fr.FrequencyList().Fe == fdp.Fe and fr.FrequencyList().N/fdp.N*fdp.N ==\
                fr.FrequencyList().N:
            return fr._Decimate(fr.FrequencyList().N/fdp.N)
        # this is the last resort.  The padded frequency response is now resampled
        # using the CZT on the impulse response
        ir=fr.ImpulseResponse()
        Ts=1./ir.TimeDescriptor().Fs
        H=ir.TimeDescriptor().H
        TD=-Ts*(-H/Ts-math.floor(-H/Ts+0.5))
        ir=ir.DelayBy(-TD)
        X=CZT(ir.Values(),ir.TimeDescriptor().Fs,0,fdp.Fe,fdp.N,highSpeed=True)
        return FrequencyResponse(fdp,X)._DelayBy(-ir.TimeDescriptor().N/2./
                                                ir.TimeDescriptor().Fs+TD)
...
