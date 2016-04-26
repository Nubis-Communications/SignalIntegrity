class FrequencyResponse(FrequencyDomain):
...
    def _Pad(self,P):
        """Pads the frequency response

        Args:
            P+1 (int) the desired number of frequency points.

        Notes:
            N+1 is the number of points in the selfs frequency response

            if P==N, the original response is returned
            if P<N, the response is truncated to P+1 frequency points
            if P>N, the response is zero padded to P+1 frequency points
        """
        fd=self.FrequencyList()
        if P == fd.N:
            # pad amount equals amount already
            X=self.Response()
        # the response needs to be padded
        elif P < fd.N:
            # padding truncates response
            X=[self.Response()[n] for n in range(P+1)]
        else:
            # padding adds zeros to the response
            X=self.Response()+[0 for n in range(P-fd.N)]
        return FrequencyResponse(EvenlySpacedFrequencyList(P*fd.Fe/fd.N,P),X)
...
