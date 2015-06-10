from numpy import fft
import math
import cmath

from SignalIntegrity.SParameters.FrequencyList import FrequencyList
from SignalIntegrity.SParameters.FrequencyList import EvenlySpacedFrequencyList
from SignalIntegrity.SParameters.FrequencyList import GenericFrequencyList
from SignalIntegrity.SParameters.ImpulseResponse import ImpulseResponse
from SignalIntegrity.TimeDomain.Waveform.TimeDescriptor import TimeDescriptor
from SignalIntegrity.Splines import Spline
from SignalIntegrity.ChirpZTransform import CZT

def Rat(R,tol=0.0001):
    N=10
    D=[]
    for n in range(N+1):
        D.append(int(math.floor(R)))
        B=R-D[n]
        if B < tol:
            break
        R = 1./B
    N = len(D)-1
    R=(1,0)
    for n in range(N+1):
        R=(R[0]*D[N-n]+R[1],R[0])
    return R

class FrequencyResponse(object):
    def __init__(self,f=None,resp=None):
        self.m_f=FrequencyList(f)
        self.m_resp=resp
    def __getitem__(self,item): return self.m_resp[item]
    def __len__(self): return len(self.m_resp)
    def FrequencyList(self):
        return self.m_f
    def Frequencies(self,unit=None):
        return self.m_f.Frequencies(unit)
    def Response(self,unit=None):
        if unit==None:
            return self.m_resp
        elif unit =='dB':
            return [20.*math.log10(abs(self.m_resp[n])) for n in range(len(self.m_f))]
        elif unit == 'mag':
            return [abs(self.m_resp[n]) for n in range(len(self.m_f))]
        elif unit == 'rad':
            return [cmath.phase(self.m_resp[n]) for n in range(len(self.m_f))]
        elif unit == 'deg':
            return [cmath.phase(self.m_resp[n])*180./math.pi for n in range(len(self.m_f))]
        elif unit == 'real':
            return [self.m_resp[n].real for n in range(len(self.m_f))]
        elif unit == 'imag':
            return [self.m_resp[n].imag for n in range(len(self.m_f))]
    def _DelayBy(self,TD):
        fd=self.FrequencyList()
        return FrequencyResponse(fd,
            [self.Response()[n]*cmath.exp(-1j*2.*math.pi*fd[n]*TD) for n in range(fd.N+1)])
    def ImpulseResponse(self,td=None,adjustDelay=True):
        """Produces the impulse response

        Args:
            td (TimeDescriptor) (optional) the time descriptor for the impulse response.
            adjustDelay (bool) whether to adjust the delay.

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
        if not evenlySpaced and td is None:
            return None
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
            t = ir.Times()
            x = ir.Values()
            idx = x.index(max(x))
            TD = t[idx] # the time of the main peak
            # calculate the frequency response with this delay taken out
            # the fractional delay is based on the minimum adjustment to the phase of the
            # last point to make that point real
            theta = self._DelayBy(-TD).Response('rad')[self.FrequencyList().N]
            if theta < -math.pi/2.: theta=-(math.pi+theta)
            elif theta > math.pi/2.: theta = math.pi-theta
            else: theta = -theta
            # calculate the fractional delay
            TD=theta/2./math.pi/self.FrequencyList()[-1]
            # take only the fractional delay now from the orignal response
            # compute this generic impulse response with the fractional delay back in
            return self._DelayBy(-TD).ImpulseResponse(None,adjustDelay=False).DelayBy(TD)
        if evenlySpaced and not td is None:
            # if td is a float and not a time descriptor, it's assumed to be a sample rate
            # in this case, we fill in the number of points in a time descriptor representing the time
            # content of self
            return self.Resample(td.FrequencyList()).ImpulseResponse()
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
##            X=[0 for n in range(P+1)]
##            for n in range(self.FrequencyList().N+1):
##                X[n]=self.Response()[n]
        return FrequencyResponse(EvenlySpacedFrequencyList(P*fd.Fe/fd.N,P),X)
    def _Decimate(self,D):
        """decimates the frequency response

        Args:
            D (int) the decimation factor.

        Notes:
            D is assumed >= 1
            N+1 is the number of points in the selfs frequency response

            N/D+1 is the number of points in the decimated frequency response
        """
        fd=self.FrequencyList()
        X=[self.Response()[n*D] for n in range(fd.N/D+1)]
        return FrequencyResponse(EvenlySpacedFrequencyList(fd.N/D*D/fd.N*fd.Fe,fd.N/D),X)
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
            # the pad amount is the same as the number of points in the impulse response
            # the frequencies are already on the grid
            fr=self
        elif P*D == K:
            # desired number of points is an integer multiple of the pad amount
            # the frequency response can be simply decimated by this multiple
            fr=self._Decimate(D)
        else:
            # the pad amount is not the same as the original impulse response and
            # the original impulse response length is not an integer multple of the
            # pad amount.  Therefore pad the impulse response and recompute the
            # frequency response
            fr=self.ImpulseResponse()._Pad(P).FrequencyResponse(None,adjustLength=False)
        # often, after padding the impulse response to get things on the right frequency scale,
        # the frequency response is just right
        if fd.N == fr.FrequencyList().N and fd.Fe == fr.FrequencyList().Fe:
            return fr
        # The frequency response in fr is now what gets resampled.  It is probably on the desired frequency grid (it might not
        # be if the pad amount got limited above.  If not, it's at the finest spacing possible.
        fr=fr._Pad(P=int(math.ceil(fd.Fe/fr.FrequencyList().Fe*fr.FrequencyList().N)))
        # the padded response might be right
        if fd.N == fr.FrequencyList().N and fd.Fe == fr.FrequencyList().Fe:
            return fr
        # now the padded frequency response is now resampled using the CZT on the impulse
        # response
        ir=fr.ImpulseResponse()
        Ts=1./ir.TimeDescriptor().Fs
        H=ir.TimeDescriptor().H
        TD=-Ts*(-H/Ts-math.floor(-H/Ts+0.5))
        ir=ir.DelayBy(-TD)
        X=CZT(ir.Values(),ir.TimeDescriptor().Fs,0,fd.Fe,fd.N,highSpeed=True)
        return FrequencyResponse(fd,X)._DelayBy(-ir.TimeDescriptor().N/2./ir.TimeDescriptor().Fs+TD)
    def ReadFromFile(self,fileName):
        with open(fileName,"rU") as f:
            data=f.readlines()
        if data[0].strip('\n')!='UnevenlySpaced':
            N = int(str(data[0]))
            Fe = float(str(data[1]))
            frl=[line.split(' ') for line in data[2:]]
            resp=[float(fr[0])+1j*float(fr[1]) for fr in frl]
            self.m_f=EvenlySpacedFrequencyList(Fe,N)
            self.m_resp=resp
        else:
            frl=[line.split(' ') for line in data[1:]]
            f=[float(fr[0]) for fr in frl]
            resp=[float(fr[1])+1j*float(fr[2]) for fr in frl]
            self.m_f=GenericFrequencyList(f)
            self.m_resp=resp
        return self
    def WriteToFile(self,fileName):
        fl=self.FrequencyList()
        with open(fileName,"w") as f:
            if fl.CheckEvenlySpaced():
                f.write(str(fl.N)+'\n')
                f.write(str(fl.Fe)+'\n')
                for v in self.Response():
                    f.write(str(v.real)+' '+str(v.imag)+'\n')
            else:
                f.write('UnevenlySpaced\n')
                for n in range(len(fl)):
                    f.write(str(fl[n])+' '+str(self.Response()[n].real)+' '+str(self.Response()[n].imag)+'\n')
        return self
    def __eq__(self,other):
        if self.FrequencyList() != other.FrequencyList():
            return False # pragma: no cover
        if len(self.Response()) != len(other.Response()):
            return False # pragma: no cover
        for k in range(len(self.Response())):
            if abs(self.Response()[k] - other.Response()[k]) > 1e-5:
                return False # pragma: no cover
        return True
    def __ne__(self,other):
        return not self == other

