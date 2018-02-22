class ImpulseResponse(Waveform):
...
    def _Pad(self,P):
        K=len(self)
        if P==K:
            x = self.Values()
        elif P<K:
            x=[self[k] for k in range((K-P)/2,K-(K-P)/2)]
        else:
            x=[0 for p in range((P-K)/2)]
            x=x+self.Values()+x
        td = self.td
        return ImpulseResponse(TimeDescriptor(td.H-(P-K)/2./td.Fs,P,td.Fs),x)
...
