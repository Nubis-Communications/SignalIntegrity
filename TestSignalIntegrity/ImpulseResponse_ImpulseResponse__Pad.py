class ImpulseResponse(Waveform):
...
    def _Pad(self,P):
        """Pads the impulse response

        Args:
            P (int) the desired number of time points.

        Notes:
            P must be even - not checked - it must add equal points to the left
            and right of the impulse response.
            K is the number of points in the selfs frequency response

            if P==K, the original response is returned
            if P<K, the response is truncated to P time points
            if P>K, the response is zero padded to P time points
        """
        K=len(self)
        if P==K:
            x = self.Values()
        elif P<K:
            x=[self.Values()[k] for k in range((K-P)/2,K-(K-P)/2)]
        else:
            x=[0 for p in range((P-K)/2)]
            x=x+self.Values()+x
        td = self.td
        return ImpulseResponse(TimeDescriptor(td.H-(P-K)/2./td.Fs,P,td.Fs),x)
...
