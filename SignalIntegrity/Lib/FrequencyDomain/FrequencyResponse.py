"""
Frequency Response
"""

# Copyright (c) 2018 Teledyne LeCroy, Inc.
# All rights reserved worldwide.
#
# This file is part of SignalIntegrity.
#
# SignalIntegrity is free software: You can redistribute it and/or modify it under the terms
# of the GNU General Public License as published by the Free Software Foundation, either
# version 3 of the License, or any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <https://www.gnu.org/licenses/>

from numpy import fft
import math
import cmath

from SignalIntegrity.Lib.FrequencyDomain.FrequencyDomain import FrequencyDomain
from SignalIntegrity.Lib.FrequencyDomain.FrequencyList import EvenlySpacedFrequencyList
from SignalIntegrity.Lib.TimeDomain.Waveform.ImpulseResponse import ImpulseResponse
from SignalIntegrity.Lib.TimeDomain.Waveform.TimeDescriptor import TimeDescriptor
from SignalIntegrity.Lib.Splines import Spline
from SignalIntegrity.Lib.ChirpZTransform import CZT
from SignalIntegrity.Lib.Rat import Rat

class FrequencyResponse(FrequencyDomain):
    """FrequencyResponse

    Frequency response view of a waveform assumed computed from the FrequencyResponse() method
    of a class ImpulseResponse, which is itself derived from the class Waveform.  In other words,
    it would contain complex frequency-domain values that, if multiplied by the values in an
    instance of class FrequencyContent, would filter the waveform in the frequency-domain.
    @see ImpulseResponse
    """
    def __init__(self,f=None,resp=None):
        """Constructor
        @param f instance of class FrequencyList
        @param resp list of complex values
        @remark
        It is assumed that the frequencies and the response provided were generated from
        the FrequencyResponse() method of the class ImpulseResponse."""
        FrequencyDomain.__init__(self,f,resp)
    def Response(self,unit=None):
        """Response
        @param unit string defining the desired units for the response.
        @return list of frequency response values in the unit specified.
        @see FrequencyDomain.Values() for valid units.
        """
        return self.Values(unit)
    def _DelayBy(self,TD):
        fd=self.FrequencyList()
        return FrequencyResponse(fd,
        [self[n]*cmath.exp(-1j*2.*math.pi*fd[n]*TD)
            for n in range(fd.N+1)])
    def ImpulseResponse(self,td=None,adjustDelay=True):
        """the time-domain impulse response
        @param td (optional) instance of class TimeDescriptor.
        @param adjustDelay (optional) bool whether to adjust the delay.
        @return instance of class ImpulseResponse corresponding to the frequency response.
        @remark
        If the optional time descriptor is supplied, the resulting impulse response is resampled
        onto that time descriptor.
        @note
        internally, the frequency response is either evenly spaced or not.

        whether evenly spaced, whether a time descriptor is specified and
        whether to adjust delay determines all possibilities.

        | evenly spaced | time descriptor | adjust delay | Situation                                         |
        |:------------: |:---------------:|:------------:|:---------------------------------------------------                                          |
        |  False        | False           | X            | Cannot be done                                    |
        |  False        | True            | X            | Spline resamples to time descriptor               |
        |  True         | False           | False        | generic impulse response                          |
        |  True         | False           | True         | impulse response with delay adjusted              |
        |  True         | True            | X            | CZT resamples to td - ad forced to T              |

        Much of these options are meant for internal use.  Mostly you should simply use ImpulseResponse()
        with the default arguments.
        @remark td can also be supplied as a float or int.  In this situation, the TimeDescriptor corresponding
        to the internal FrequencyList is used, but the td supplied supplants the sample rate of the TimeDescriptor.
        In this way, only the sample rate can be specified in the resampling, and all processing as shown in the
        table above will assume that a time descriptor has been supplied of this calculated type.
        """
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
            return newfr.ImpulseResponse(None,adjustDelay)
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
            return ImpulseResponse(td,Y)
        if evenlySpaced and td is None and adjustDelay:
            TD=self._FractionalDelayTime()
            return self._DelayBy(-TD).ImpulseResponse(None,False).DelayBy(TD)
        if evenlySpaced and not td is None:
            # if td is a float and not a time descriptor, it's assumed to be a
            # sample rate.  In this case, the number of points in a
            # time descriptor are filled in representing the time content of self
            return self.Resample(td.FrequencyList()).ImpulseResponse()
    def _Pad(self,P):
        """Pads the frequency response
        @param P int number of frequency points to pad to (-1)
        @note N+1 is the number of points in the selfs frequency response.
        if P==N, the original response is returned.
        if P<N, the response is truncated to P+1 frequency points.
        if P>N, the response is zero padded to P+1 frequency points.
        """
        fd=self.FrequencyList()
        if P == fd.N: X=self.Response()
        elif P < fd.N: X=[self.Response()[n] for n in range(P+1)]
        else: X=self.Response()+[0 for n in range(P-fd.N)]
        return FrequencyResponse(EvenlySpacedFrequencyList(P*fd.Fe/fd.N,P),X)
    def _Decimate(self,D):
        """decimates the frequency response
        @param D integer decimation factor.
        @note D is assumed >= 1.
        N+1 is the number of points in the selfs frequency response.
        N/D+1 is the number of points in the decimated frequency response.
        """
        fd=self.FrequencyList()
        X=[self.Response()[n*D] for n in range(fd.N//D+1)]
        return FrequencyResponse(EvenlySpacedFrequencyList(fd.N//D*D//fd.N*fd.Fe,fd.N//D),X)
    def _SplineResample(self,fdp):
        fd=self.FrequencyList()
        Poly=Spline(fd,self.Response())
        newresp=[Poly.Evaluate(f) if f <= fd[-1] else 0.0001 for f in fdp]
        return FrequencyResponse(fdp,newresp)
    def Resample(self,fdp):
        """Resamples to a different set of frequencies
        @param fdp instance of class FrequencyList to resample to
        @return instance of class FrequencyResponse containing resampled self
        @remark
        Resampling first attempts to find a ratio of numbers of points
        to resample to.  If a reasonable ratio is found, pure DFT and IDFT
        methods are utilized along with padding and decimation.

        Otherwise, the chirp z transform is used to resample.

        If the points are unevenly spaced, there is no choice but to resample with
        splines.

        @see FrequencyResponse.ResampleCZT()
        @see Spline
        """
        fd=self.FrequencyList()
        evenlySpaced = fd.CheckEvenlySpaced() and fdp.CheckEvenlySpaced()
        if not evenlySpaced: return self._SplineResample(fdp)
        R=Rat(fd.Fe/fdp.Fe*fdp.N); ND1=R[0]; D2=R[1]
        if ND1 < fd.N: R=Rat(fd.Fe/fdp.Fe*fdp.N/fd.N); ND1=R[0]*fd.N; D2=R[1]
        if  ND1 > 50000: return self.ResampleCZT(fdp)
        if ND1 == fd.N: fr=self
        else: fr=self.ImpulseResponse()._Pad(2*ND1).FrequencyResponse(None,False)
        if D2*fdp.N != ND1: fr=fr._Pad(D2*fdp.N)
        if D2==1: return fr
        else: return fr._Decimate(D2)
    def _FractionalDelayTime(self):
        ir = self.ImpulseResponse(None,adjustDelay=False)
        idx = ir.Values('abs').index(max(ir.Values('abs')))
        TD = ir.td[idx] # the time of the main peak
        # calculate the frequency response with this delay taken out
        # the fractional delay is based on the minimum adjustment to the phase of
        # the last point to make that point real
        theta = self._DelayBy(-TD).Response('rad')[self.FrequencyList().N]
        # do not make this adjustment if the phase is of a tiny magnitude!
        if self.Response('dB')[self.FrequencyList().N]<-90: theta=0.
        if theta < -math.pi/2.: theta=-(math.pi+theta)
        elif theta > math.pi/2.: theta = math.pi-theta
        else: theta = -theta
        # calculate the fractional delay
        TD=theta/2./math.pi/self.FrequencyList()[-1]
        return TD
    def ResampleCZT(self,fdp,speedy=True):
        """Uses the chirp z transform is used to resample.
        @param fdp instance of class FrequencyList to resample to
        @param speedy (optional) bool whether to use the fast version of the CZT()
        @return instance of class FrequencyResponse containing resampled self
        @see FrequencyResponse.Resample()
        @see CZT()
        """
        fd=self.FrequencyList()
        evenlySpaced = fd.CheckEvenlySpaced() and fdp.CheckEvenlySpaced()
        if not evenlySpaced: return self._SplineResample(fdp)
        ir=self.ImpulseResponse()
        TD=ir._FractionalDelayTime()
        Ni=int(min(math.floor(fd.Fe*fdp.N/fdp.Fe),fdp.N))
        Fei=Ni*fdp.Fe/fdp.N
        return FrequencyResponse(EvenlySpacedFrequencyList(Fei,Ni),
            CZT(ir.DelayBy(-TD).Values(),ir.td.Fs,0,Fei,Ni,speedy)).\
            _Pad(fdp.N)._DelayBy(-fd.N/2./fd.Fe+TD)
