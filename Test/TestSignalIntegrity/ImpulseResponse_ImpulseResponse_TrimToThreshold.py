class ImpulseResponse(Waveform):
...
    def TrimToThreshold(self,threshold):
        x=self.Values()
        td=self.td
        maxabsx=max(self.Values('abs'))
        minv=maxabsx*threshold
        for k in range(len(x)):
            if abs(x[k]) >= minv:
                startidx = k
                break
        for k in range(len(x)):
            ki = len(x)-1-k
            if abs(x[ki]) >= minv:
                endidx = ki
                break
        if (endidx-startidx+1)//2*2 != endidx-startidx+1:
            # the result would not have an even number of points
            if endidx < len(x)-1:
                # keep a point at the end if possible
                endidx = endidx + 1
            elif startidx > 0:
                # keep a point at the beginning if possible
                startidx = startidx - 1
            else:
                # append a zero to the end and calculate number of
                # points with endidx+1
                return ImpulseResponse(TimeDescriptor(td[startidx],
                    (endidx+1)-startidx+1,td.Fs),
                    [x[k] for k in range(startidx,endidx+1)]+[0.])
        return ImpulseResponse(TimeDescriptor(td[startidx],
            endidx-startidx+1,td.Fs),
            [x[k] for k in range(startidx,endidx+1)])
...
