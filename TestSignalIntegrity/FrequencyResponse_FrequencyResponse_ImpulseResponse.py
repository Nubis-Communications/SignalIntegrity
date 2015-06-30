class FrequencyResponse(object):
...
    def ImpulseResponse(self,td=None,adjustDelay=True):
        """Produces the impulse response

        Args:
            td (TimeDescriptor) (optional) desired time descriptor.
            adjustDelay (bool) (optional) whether to adjust the delay.

        Notes:
            internally, the frequency response is either evenly spaced or not.

            whether evenly spaced, whether a time descriptor is specified and whether
            to adjust delay determines all possibilities of what can happen.

            es  td  ad
            F   F   X   Cannot be done
            F   T   X   Spline resamples to td and returns es=T,td=F,ad
            T   F   F   generic impulse response
            T   F   T   impulse response with delay adjusted
            T   T   X   CZT resamples to td - ad forced to T
        """
        fd = self.FrequencyList()
        if isinstance(td,float) or isinstance(td,int):
            Fs=float(td)
            td=fd.TimeDescriptor()
            td = TimeDescriptor(0.,2*int(math.ceil(Fs*td.N/2./td.Fs)),Fs)
        evenlySpaced = fd.CheckEvenlySpaced()
        if not evenlySpaced and td is None: return None
        if not evenlySpaced and not td is None:
            newfd = td.FrequencyList()
            oldfd = fd
            Poly=Spline(oldfd,self.Response())
            newresp=[Poly.Evaluate(f) if f <= oldfd[-1] else 0.0001 for f in newfd]
            newfr=FrequencyResponse(newfd,newresp)
            return newfr.ImpulseResponse(None,adjustDelay)
        if evenlySpaced and td is None and not adjustDelay:
            yfp=self.Response()
            ynp=[yfp[fd.N-nn].conjugate() for nn in range(1,fd.N)]
            y=yfp+ynp
            y[0]=y[0].real
            y[fd.N]=y[fd.N].real
            Y=fft.ifft(y)
            td=fd.TimeDescriptor()
            tp=[Y[k].real for k in range(td.N/2)]
            tn=[Y[k].real for k in range(td.N/2,td.N)]
            Y=tn+tp
            return ImpulseResponse(td,Y)
        if evenlySpaced and td is None and adjustDelay:
            ir = self.ImpulseResponse(None,adjustDelay=False)
            idx = ir.Values('abs').index(max(ir.Values('abs')))
            TD = ir.Times()[idx] # the time of the main peak
            # calculate the frequency response with this delay taken out
            # the fractional delay is based on the minimum adjustment to the phase of
            # the last point to make that point real
            theta = self._DelayBy(-TD).Response('rad')[self.FrequencyList().N]
            if theta < -math.pi/2.: theta=-(math.pi+theta)
            elif theta > math.pi/2.: theta = math.pi-theta
            else: theta = -theta
            # calculate the fractional delay
            TD=theta/2./math.pi/self.FrequencyList()[-1]
            # take only the fractional delay now from the original response
            # compute this generic impulse response with the fractional delay back in
            return self._DelayBy(-TD).ImpulseResponse(None,False).DelayBy(TD)
        if evenlySpaced and not td is None:
            # if td is a float and not a time descriptor, it's assumed to be a sample
            # rate.  In this case, we fill in the number of points in a time descriptor
            # representing the time content of self
            return self.Resample(td.FrequencyList()).ImpulseResponse()
...
