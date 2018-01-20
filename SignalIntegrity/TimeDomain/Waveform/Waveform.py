'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
from numpy import fft
from copy import copy

from TimeDescriptor import TimeDescriptor
from AdaptedWaveforms import AdaptedWaveforms
from SignalIntegrity.PySIException import PySIExceptionWaveformFile,PySIExceptionWaveform

class Waveform(object):
    adaptionStrategy='SinX'
    def __init__(self,x=None,y=None):
        if isinstance(x,Waveform):
            self.m_t=x.m_t
            self.m_y=x.m_y
        elif isinstance(x,TimeDescriptor):
            self.m_t=x
            if isinstance(y,list):
                self.m_y=y
            elif isinstance(y,(float,int,complex)):
                self.m_y=[y.real for k in range(x.N)]
            else:
                self.m_y=[0 for k in range(x.N)]
        else:
            self.m_t=None
            self.m_y=None
    def __len__(self):
        return len(self.m_y)
    def __getitem__(self,item):
        return self.m_y[item]
    def __setitem__(self,item,value):
        self.m_y[item]=value
        return self
    def Times(self,unit=None):
        return self.m_t.Times(unit)
    def TimeDescriptor(self):
        return self.m_t
    def Values(self,unit=None):
        if unit==None:
            return self.m_y
        elif unit =='abs':
            return [abs(y) for y in self.m_y]
    def OffsetBy(self,v):
        self.m_y = [y+v for y in self.m_y]
        return self
    def DelayBy(self,d):
        return Waveform(self.TimeDescriptor().DelayBy(d),self.Values())
    def __add__(self,other):
        if isinstance(other,Waveform):
            if self.TimeDescriptor() == other.TimeDescriptor():
                return Waveform(self.TimeDescriptor(),[self[k]+other[k] for k in range(len(self))])
            else:
                [s,o]=AdaptedWaveforms([self,other])
                return Waveform(s.TimeDescriptor(),[s[k]+o[k] for k in range(len(s))])
                #return awf[0]+awf[1]
        elif isinstance(other,(float,int,complex)):
            return Waveform(self.m_t,[v+other.real for v in self.Values()])
        # pragma: silent exclude
        else:
            raise PySIExceptionWaveform('cannot add waveform to type '+str(other.__class__.__name__))
        # pragma: include
    def __sub__(self,other):
        if isinstance(other,Waveform):
            if self.TimeDescriptor() == other.TimeDescriptor():
                return Waveform(self.TimeDescriptor(),[self[k]-other[k] for k in range(len(self))])
            else:
                [s,o]=AdaptedWaveforms([self,other])
                return Waveform(s.TimeDescriptor(),[s[k]-o[k] for k in range(len(s))])
        elif isinstance(other,(float,int,complex)):
            return Waveform(self.m_t,[v-other.real for v in self.Values()])
        # pragma: silent exclude
        else:
            raise PySIExceptionWaveform('cannot subtract type' + +str(other.__class__.__name__) + ' from waveform')
        # pragma: include
    def __radd__(self, other):
        if other == 0:
            return self
        else:
            return self.__add__(other)
    def __mul__(self,other):
        # pragma: silent exclude
        from SignalIntegrity.TimeDomain.Filters.FirFilter import FirFilter
        from SignalIntegrity.TimeDomain.Filters.WaveformTrimmer import WaveformTrimmer
        from SignalIntegrity.TimeDomain.Filters.WaveformDecimator import WaveformDecimator
        # pragma: include
        if isinstance(other,FirFilter):
            return other.FilterWaveform(self)
        elif isinstance(other,WaveformTrimmer):
            return other.TrimWaveform(self)
        elif isinstance(other,WaveformDecimator):
            return other.DecimateWaveform(self)
        elif isinstance(other,(float,int,complex)):
            return Waveform(self.m_t,[v*other.real for v in self.Values()])
        # pragma: silent exclude
        else:
            raise PySIExceptionWaveform('cannot multiply waveform by type '+str(other.__class__.__name__))
        # pragma: include
    def __div__(self,other):
        if isinstance(other,(float,int,complex)):
            return Waveform(self.m_t,[v/other.real for v in self.Values()])
        # pragma: silent exclude
        else:
            raise PySIExceptionWaveform('cannot divide waveform by type '+str(other.__class__.__name__))
        # pragma: include
    def ReadFromFile(self,fileName):
        # pragma: silent exclude outdent
        try:
        # pragma: include
            with open(fileName,"rU") as f:
                data=f.readlines()
                HorOffset=float(data[0])
                NumPts=int(float(data[1])+0.5)
                SampleRate=float(data[2])
                Values=[float(data[k+3]) for k in range(NumPts)]
            self.m_t=TimeDescriptor(HorOffset,NumPts,SampleRate)
            self.m_y=Values
        # pragma: silent exclude indent
        except IOError:
            raise PySIExceptionWaveformFile(fileName+' not found')
        # pragma: include
        return self
    def WriteToFile(self,fileName):
        with open(fileName,"w") as f:
            td=self.TimeDescriptor()
            f.write(str(td.H)+'\n')
            f.write(str(int(td.N))+'\n')
            f.write(str(td.Fs)+'\n')
            for v in self.Values():
                f.write(str(v)+'\n')
        return self
    def __eq__(self,other):
        if self.TimeDescriptor() != other.TimeDescriptor():
            return False
        if len(self.Values()) != len(other.Values()):
            return False
        for k in range(len(self.Values())):
            if abs(self.Values()[k]-other.Values()[k])>1e-6:
                return False
        return True
    def __ne__(self,other):
        return not self == other
    def Adapt(self,td):
        # pragma: silent exclude
        from SignalIntegrity.TimeDomain.Filters.InterpolatorSinX import InterpolatorSinX
        from SignalIntegrity.TimeDomain.Filters.InterpolatorSinX import FractionalDelayFilterSinX
        from SignalIntegrity.TimeDomain.Filters.InterpolatorLinear import InterpolatorLinear
        from SignalIntegrity.TimeDomain.Filters.InterpolatorLinear import FractionalDelayFilterLinear
        from SignalIntegrity.TimeDomain.Filters.WaveformTrimmer import WaveformTrimmer
        from SignalIntegrity.TimeDomain.Filters.WaveformDecimator import WaveformDecimator
        from SignalIntegrity.Rat import Rat
        # pragma: include
        wf=self
        (upsampleFactor,decimationFactor)=Rat(td.Fs/wf.TimeDescriptor().Fs)
        if upsampleFactor>1:
            wf=wf*(InterpolatorSinX(upsampleFactor) if wf.adaptionStrategy=='SinX'
                else InterpolatorLinear(upsampleFactor))
        ad=td/wf.TimeDescriptor()
        f=ad.D-int(ad.D)
        if not f==0.0:
            wf=wf*(FractionalDelayFilterSinX(f,True) if wf.adaptionStrategy=='SinX'
                else FractionalDelayFilterLinear(f,True))
            ad=td/wf.TimeDescriptor()
        if decimationFactor>1:
            decimationPhase=int(round(ad.TrimLeft())) % decimationFactor
            wf=wf*WaveformDecimator(decimationFactor,decimationPhase)
            ad=td/wf.TimeDescriptor()
        tr=WaveformTrimmer(max(0,int(round(ad.TrimLeft()))),
                           max(0,int(round(ad.TrimRight()))))
        wf=wf*tr
        return wf
    def Measure(self,time):
        for i in range(len(self.m_t)):
            if self.m_t[i] > time:
                v = (time - self.m_t[i-1])/(self.m_t[i]-self.m_t[i-1])*\
                (self.m_y[i]-self.m_y[i-1])+self.m_y[i-1]
                return v
    def FrequencyContent(self,fd=None):
        # pragma: silent exclude
        from SignalIntegrity.FrequencyDomain.FrequencyContent import FrequencyContent
        # pragma: include
        return FrequencyContent(self,fd)
    def Integral(self,c=0.,addPoint=True,scale=True):
        td=copy(self.TimeDescriptor())
        i=[0 for k in range(len(self))]
        T=1./td.Fs if scale else 1.
        for k in range(len(i)):
            if k==0:
                i[k]=self[k]*T+c
            else:
                i[k]=i[k-1]+self[k]*T
        td.H=td.H+(1./2.)*(1./td.Fs)
        if addPoint:
            td.N=td.N+1
            td.H=td.H=td.H-1./td.Fs
            i=[c]+i
        return Waveform(td,i)
    def Derivative(self,c=0.,removePoint=True,scale=True):
        td=copy(self.TimeDescriptor())
        vl=copy(self.Values())
        v=self.Values()
        T=1./td.Fs if scale else 1.
        for k in range(len(vl)):
            if k==0:
                vl[k]=0.
            else:
                vl[k]=(v[k]-v[k-1])/T
        td.H=td.H-(1./2.)*(1./td.Fs)
        if removePoint:
            td.N=td.N-1
            td.H=td.H+1./td.Fs
            vl=vl[1:]
        return Waveform(td,vl)

class WaveformFileAmplitudeOnly(Waveform):
    def __init__(self,fileName,td=None):
        if not td is None:
            HorOffset=td.H
            NumPts=td.N
            SampleRate=td.Fs
        else:
            HorOffset=0.0
            NumPts=0
            SampleRate=1.
        with open(fileName,'rb') as f:
            wf = [float(line) for line in f]
        if NumPts==0:
            NumPts=len(wf)
        else:
            if len(wf) > NumPts:
                wf = [wf[k] for k in range(NumPts)]
            else:
                NumPts=len(wf)
        Waveform.__init__(self,TimeDescriptor(HorOffset,NumPts,SampleRate),wf)