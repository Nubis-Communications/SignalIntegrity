class ImpulseResponse(Waveform):
...
    def _Pad(self,P):
        K=len(self)
        if P==K: x = self.Values()
        elif P<K: x=self.values[(K-P)//2:K-(K-P)//2]
        else:
            pad=np.zeros((P-K)//2,dtype=self.values.dtype)
            x=np.concatenate((pad,self.values,pad))
        td = self.td
        return ImpulseResponse(TimeDescriptor(td.H-(P-K)/2./td.Fs,P,td.Fs),x)
...
