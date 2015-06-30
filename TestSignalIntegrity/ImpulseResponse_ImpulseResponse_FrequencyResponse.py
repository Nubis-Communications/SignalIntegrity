class ImpulseResponse(Waveform):
...
    def FrequencyResponse(self,fd=None,adjustLength=True):
        """Produces the frequency response

        Args:
            fd (FrequencyDescriptor) (optional) the desired frequency descriptor.
            adjustLength (bool) (optional) whether to adjust the length.
                defaults to True

        Notes:
            All impulse responses are evenly spaced

            whether a frequency descriptor is specified and whether
            to adjust length determines all possibilities of what can happen.

            fd  al
            F   F   generic frequency response
            F   T   frequency response with length adjusted
            T   X   CZT resamples to fd (length is adjusted first)
        """
        from SignalIntegrity.SParameters.FrequencyResponse import FrequencyResponse
        if not fd and not adjustLength:
            X=fft.fft(self.Values())
            fd=self.TimeDescriptor().FrequencyList()
            return FrequencyResponse(fd,[X[n] for n in range(fd.N+1)]).\
                _DelayBy(self.TimeDescriptor().H)
        if not fd and adjustLength:
            return self._AdjustLength().FrequencyResponse(None,adjustLength=False)
        if fd:
            return self.FrequencyResponse().Resample(fd)
    def _AdjustLength(self):
        td = self.TimeDescriptor()
        PositivePoints = int(max(0,math.floor(td.H*td.Fs+td.N+0.5)))
        NegativePoints = int(max(0,math.floor(-td.H*td.Fs+0.5)))
        P=max(PositivePoints,NegativePoints)*2
        return self._Pad(P)
...
