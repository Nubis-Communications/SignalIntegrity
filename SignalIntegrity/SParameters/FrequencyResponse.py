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
    def DelayBy(self,TD):
        fd=self.FrequencyList()
        return FrequencyResponse(fd,
            [self.Response()[n]*cmath.exp(-1j*2.*math.pi*fd[n]*TD) for n in range(fd.N+1)])
    def ImpulseResponse2(self,td=None,adjustDelay=False):
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
        evenlySpaced = fd.CheckEvenlySpaced()
        if not evenlySpaced and td is None:
            raise Error
        if not evenlySpaced and not td is None:
            newfd = td.FrequencyDescriptor()
            oldfd = fd
            Poly=Spline(oldfd,self.Response())
            newresp=[Poly.Evaluate(f) if f <= oldfd[-1] else 0.0001 for f in newfd]
            newfr=FrequencyResponse(newfd,newresp)
            return newfr.ImpulseResponse2(None,adjustDelay)
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
            ir = self.ImpulseResponse2()
            t = ir.Times()
            x = ir.Values()
            acc = abs(x[0])
            idx = 0
            for k in range(len(t)):
                if abs(x[k])>acc:
                    acc=x[k]
                    idx=k
            TD = t[idx] # the time of the main peak
            # calculate the frequency response with this delay taken out
            # the fractional delay is based on the minimum adjustment to the phase of the
            # last point to make that point real
            theta = self.DelayBy(-TD).Response('rad')[self.FrequencyList().N]
            if theta < -math.pi/2.:
                theta=-(math.pi+theta)
            elif theta > math.pi/2.:
                theta = math.pi-theta
            else:
                theta = -theta
            # calculate the fractional delay
            TD=theta/2./math.pi/self.FrequencyList()[-1]
            # take only the fractional delay now from the orignal response
            # compute this generic impulse response with the fractional delay back in
            return self.DelayBy(-TD).ImpulseResponse2().DelayBy(TD)
        if evenlySpaced and not td is None:
            fr = self.Resample2(td.FrequencyList())
            return fr.ImpulseResponse2(None,adjustDelay=True)
    def Resample2(self,fd):
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
            X=[self.Response()[n*D] for n in range(self.FrequencyList().N/D+1)]
            fr=FrequencyResponse(EvenlySpacedFrequencyList(self.FrequencyList().Fe,self.FrequencyList().N/D),X)
        else:
            # the pad amount is not the same as the original impulse response and
            # the original impulse response length is not an integer multple of the
            # pad amount.  Therefore pad the impulse response and recompute the
            # frequency response
            ir=self.ImpulseResponse2(None,adjustDelay=True)
            K=len(ir)
            if P<K:
                x=[ir.Values()[k] for k in range((K-P)/2,K-(K-P)/2)]
            else: # P>K
                x=[0 for p in range(P)]
                for k in range(K):
                    x[k+(P-K)/2]=ir.Values()[k]
            ir=ImpulseResponse(TimeDescriptor(ir.TimeDescriptor().H-(P-K)/2./ir.TimeDescriptor().Fs,P,ir.TimeDescriptor().Fs),x)
            fr=ir.FrequencyResponse2(None,adjustDelay=True)
            del ir
        # often, after padding the impulse response to get things on the right frequency scale,
        # the frequency response is just right
        if fd.N == fr.FrequencyList().N and fd.Fe == fr.FrequencyList().Fe:
            return fr
        # The frequency response in fr is now what gets resampled.  It is probably on the desired frequency grid (it might not
        # be if the pad amount got limited above.  If not, it's at the finest spacing possible.
        P=int(math.ceil(fd.Fe/fr.FrequencyList().Fe*fr.FrequencyList().N))
        if P != fr.FrequencyList().N:
            # the response needs to be padded
            if P<fr.FrequencyList().N:
                X=[fr.Response()[n] for n in range(P)]
            else: # P>K
                X=[0 for n in range(P+1)]
                for n in range(fr.FrequencyList().N+1):
                    X[n]=fr.Response()[n]
            fr=FrequencyResponse(EvenlySpacedFrequencyList(P*fr.FrequencyList().Fe/fr.FrequencyList().N,P),X)
        # the padded response might be right
        if fd.N == fr.FrequencyList().N and fd.Fe == fr.FrequencyList().Fe:
            return fr
        # now the padded frequency response is now resampled using the CZT on the impulse
        # response
        ir=fr.ImpulseResponse2(None,adjustDelay=True)
        Ts=1./ir.TimeDescriptor().Fs
        H=ir.TimeDescriptor().H
        TD=-Ts*(-H/Ts-math.floor(-H/Ts+0.5))
        ir=ir.DelayBy(-TD)
        X=CZT(ir.Values(),ir.TimeDescriptor().Fs,0,fd.Fe,fd.N)
        return FrequencyResponse(fd,
            [X[n]*cmath.exp(-1j*2.*math.pi*fd[n]*-ir.TimeDescriptor().N/2./ir.TimeDescriptor().Fs+TD)
                for n in range(fd.N+1)])
    def ImpulseResponse(self,td=None,**args):
        from SignalIntegrity.SParameters.ResampledFrequencyResponse import ResampledFrequencyResponse
        if not td is None:
            fr=ResampledFrequencyResponse(self,td.FrequencyList(),**args)
        else:
            fr=self
        adjustDelay = args['adjustDelay'] if 'adjustDelay' in args else False
        fd=fr.FrequencyList()
        td=fd.TimeDescriptor()
        TD = cmath.phase(self[-1])/(2.*math.pi*fd[-1]) if adjustDelay else 0.
        td.DelayBy(-TD)
        N=fd.N
        K=2*N
        yfp=[fr.m_resp[n]*cmath.exp(-1j*2.*math.pi*fd[n]*TD) for n in range(N+1)]
        ynp=[yfp[N-nn].conjugate() for nn in range(1,N)]
        y=yfp+ynp
        y[0]=y[0].real
        y[N]=y[N].real
        Y=fft.ifft(y)
        tp=[Y[k].real for k in range(K/2)]
        tn=[Y[k].real for k in range(K/2,K)]
        Y=tn+tp
        return ImpulseResponse(td,Y)
    def Resample(self,fl,**args):
        from SignalIntegrity.SParameters.ResampledFrequencyResponse import ResampledFrequencyResponse
        self = ResampledFrequencyResponse(self,fl,**args)
        return self
    def ReadFromFile(self,fileName):
        with open(fileName,"rU") as f:
            data=f.readlines()
        if data[0].strip('\n')=='EvenlySpaced':
            N = int(str(data[1]))
            Fe = float(str(data[2]))
            resp=[complex(v) for v in data[3:]]
            self.m_f=EvenlySpacedFrequencyList(Fe,N)
            self.m_resp=resp
        else:
            frl=[line.split(' ') for line in data[0:]]
            f=[float(fr[0]) for fr in frl]
            resp=[complex(fr[1] for fr in frl)]
            self.m_f=GenericFrequencyList(f)
        return self
    def WriteToFile(self,fileName):
        fl=self.FrequencyList()
        with open(fileName,"w") as f:
            if fl.CheckEvenlySpaced():
                f.write('EvenlySpaced\n')
                f.write(str(fl.N)+'\n')
                f.write(str(fl.Fe)+'\n')
                for v in self.Response():
                    f.write(str(v)+'\n')
            else:
                for n in len(fl):
                    f.write(str(fl[n])+' '+str(self.Response()[n])+'\n')
        return self
    def __eq__(self,other):
        if self.FrequencyList() != other.FrequencyList():
            return False
        if len(self.Response()) != len(other.Response()):
            return False
        for k in range(len(self.Response())):
            if abs(self.Response()[k] - other.Response()[k]) > 1e-5:
                return False
        return True
    def __ne__(self,other):
        return not self == other

