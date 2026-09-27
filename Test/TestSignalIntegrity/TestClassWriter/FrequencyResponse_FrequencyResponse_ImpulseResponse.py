class FrequencyResponse(FrequencyDomain):
    def ImpulseResponse(self,td=None,adjustDelay=True,time_before_0=None):
        fd = self.FrequencyList()
        if isinstance(td,float) or isinstance(td,int):
            Fs=float(td)
            td=fd.TimeDescriptor()
            td = TimeDescriptor(0.,2*int(math.ceil(Fs*td.K/2./td.Fs)),Fs)
        evenlySpaced = fd.CheckEvenlySpaced()
        if not evenlySpaced and td is None: return None
        if not evenlySpaced and not td is None:
            newfd = td.FrequencyList()
            oldfd = fd
            Poly=Spline(oldfd,self.Response())
            newresp=[Poly.Evaluate(f) if f <= oldfd[-1] else 0.0001 for f in newfd]
            newfr=FrequencyResponse(newfd,newresp)
            return newfr.ImpulseResponse(None,adjustDelay).Circulate(time_before_0)
        if evenlySpaced and td is None and not adjustDelay:
            yfp=self.Response()
            ynp=[yfp[fd.N-nn].conjugate() for nn in range(1,fd.N)]
            y=yfp+ynp
            y[0]=y[0].real
            y[fd.N]=y[fd.N].real
            Y=fft.ifft(y)
            td=fd.TimeDescriptor()
            tp=[Y[k].real for k in range(td.K//2)]
            tn=[Y[k].real for k in range(td.K//2,td.K)]
            Y=tn+tp
            return ImpulseResponse(td,Y).Circulate(time_before_0)
        if evenlySpaced and td is None and adjustDelay:
            TD=self._FractionalDelayTime()
            return self._DelayBy(-TD).ImpulseResponse(None,False).\
                DelayBy(TD).Circulate(time_before_0)
        if evenlySpaced and not td is None:
            # if td is a float and not a time descriptor, it's assumed to be a
            # sample rate.  In this case, the number of points in a
            # time descriptor are filled in representing the time content of self
            return self.Resample(td.FrequencyList()).\
                ImpulseResponse().Circulate(time_before_0)
...
