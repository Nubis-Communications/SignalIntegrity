"""
Waveform.py
"""

# Copyright (c) 2021 Nubis Communications, Inc.
# Copyright (c) 2018-2020 Teledyne LeCroy, Inc.
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

from copy import copy
import math
import sys
import os

import numpy as np

from SignalIntegrity.Lib.TimeDomain.Waveform.TimeDescriptor import TimeDescriptor
from SignalIntegrity.Lib.TimeDomain.Waveform.AdaptedWaveforms import AdaptedWaveforms
from SignalIntegrity.Lib.Exception import SignalIntegrityExceptionWaveformFile,SignalIntegrityExceptionWaveform
from SignalIntegrity.Lib.TimeDomain.Waveform.LeCroyWaveform import to_trc,from_trc

class Waveform(object):
    """base class for all waveforms

    @note the waveform values are stored internally as a one-dimensional numpy
    array (`self.values`); the class provides a sequence-like interface
    (indexing, iteration, len) over those values, and `numpy` interoperability
    via `__array__` (so `numpy.asarray(waveform)` yields the values array).
    """
    adaptionStrategy='SinX'
    epsilon=1e-6
    maximumWaveformSize=20e6
    def __init__(self,x=None,y=None):
        """constructor
        @param x instance of class Waveform or TimeDescriptor
        @param y numpy array or list of float/int/complex (or a single
        float/int/complex) of values

        @note here are the outcomes for this constructor:

        |x type          |y type                      |outcome                                            |
        |:--------------:|:--------------------------:|:------------------------------------------------- |
        | Waveform       | don't care                 | waveform is x provided (copy constructor)         |
        | TimeDescriptor | array/list                 | waveform with td=x and values provided            |
        | TimeDescriptor | int,float,complex          | waveform with td=x and array of constants provided|
        | TimeDescriptor | None                       | waveform with td=x and array of zeros             |
        | other (None)   | don't care (None)          | empty, uninitialized waveform                     |
        """
        if isinstance(x,Waveform):
            self.td=x.td
            self.values=np.array(x.values,copy=True)
        elif isinstance(x,TimeDescriptor):
            self.td=x
            if y is None:
                self.values=np.zeros(int(x.K))
            elif isinstance(y,(float,int,complex)):
                self.values=np.full(int(x.K),y.real,dtype=float)
            else:
                self.values=Waveform._coerce(y)
        else:
            self.td=None
            self.values=np.array([],dtype=float)
    @staticmethod
    def _coerce(y):
        """coerces a sequence of values to a one-dimensional numpy array.
        @param y sequence (numpy array, list, tuple) of values
        @return numpy array of dtype float64, or complex128 if any value is complex
        """
        a=np.asarray(y)
        if a.dtype==object:
            a=np.array([complex(v) if isinstance(v,complex) else float(v) for v in y])
        return a.astype(np.complex128) if np.iscomplexobj(a) else a.astype(np.float64)
    def __len__(self):
        """@return int number of values (points) in the waveform"""
        return len(self.values)
    def __getitem__(self,index):
        """indexing into the waveform values
        @param index int index or slice
        @return numpy scalar for an int index, or numpy array for a slice
        """
        return self.values[index]
    def __setitem__(self,index,value):
        """assignment into the waveform values
        @param index int index or slice
        @param value value(s) to assign
        """
        self.values[index]=value
    def __iter__(self):
        """@return iterator over the waveform values"""
        return iter(self.values)
    def __array__(self,dtype=None,copy=None):
        """numpy array interface
        @param dtype (optional) requested numpy dtype
        @param copy (optional) numpy 2.0 copy semantics
        @return the internal numpy values array (cast to dtype if provided)
        @note this lets numpy.asarray(waveform) and numpy ufuncs operate directly
        on the waveform's values.
        """
        arr=self.values if dtype is None else self.values.astype(dtype)
        if copy:
            arr=np.array(arr,copy=True)
        return arr
    def __copy__(self):
        """shallow copy that gives the copy its own values array
        @return instance of the same class with copied values and shared metadata
        """
        n=self.__class__.__new__(self.__class__)
        n.__dict__.update(self.__dict__)
        n.values=np.array(self.values,copy=True)
        return n
    def __deepcopy__(self,memo):
        """deep copy
        @return instance of the same class with deep-copied attributes
        """
        from copy import deepcopy
        n=self.__class__.__new__(self.__class__)
        for k,v in self.__dict__.items():
            n.__dict__[k]=deepcopy(v,memo)
        return n
    def Times(self,unit=None):
        """time values
        @param unit (optional) string containing unit for time values.
        @return list of time values
        @see TimeDescriptor for valid time units and return type.
        """
        return self.td.Times(unit)
    def TimeDescriptor(self):
        """time descriptor
        @return instance of class TimeDescriptor inherent to the waveform"""
        return self.td
    def Values(self,unit=None):
        """values
        returns the waveform values as a numpy array
        @param unit (optional) string containing unit for the values
        @note valid waveform units are:
        - None - numpy array of values returned
        -'abs' - numpy array of absolute values returned
        """
        if unit==None:
            return self.values.copy()
        elif unit =='abs':
            return np.abs(self.values)
    def OffsetBy(self,v):
        """offset by a dc value
        @param v float amount to offset the waveform by
        @return self
        @todo this is inconsistent and should be removed
        """
        self.values=self.values+v
        return self
    def DelayBy(self,d):
        """delay waveform
        @param d float amount to delay by
        @return instance of class waveform containing self delay by d
        @note does not affect self
        """
        return Waveform(self.td.DelayBy(d),self.Values())
    def __add__(self,other):
        """overloads +
        @param other instance of class Waveform or float, int, complex to add.
        @return instance of class Waveform with other added to self
        @note does not affect self
        @note
        valid types of other to add are:

        - Waveform - if the other waveform has the same time descriptor, returns the waveform
        with self and others values added together, otherwise adapts other to self and then
        adds them.
        - float,int,complex - adds the constant value to all values in self.
        @throw SignalIntegrityExceptionWaveform if other cannot be added.
        @see AdaptedWaveforms
        """
        if isinstance(other,Waveform):
            if self.td == other.td:
                return Waveform(self.td,self.values+other.values)
            else:
                [s,o]=AdaptedWaveforms([self,other])
                return Waveform(s.td,s.values+o.values)
                #return awf[0]+awf[1]
        elif isinstance(other,(float,int,complex)):
            return Waveform(self.td,self.values+other.real)
        # pragma: silent exclude
        else:
            raise SignalIntegrityExceptionWaveform('cannot add waveform to type '+str(other.__class__.__name__))
        # pragma: include
    def __sub__(self,other):
        """overloads -
        @param other instance of class Waveform or float, int, complex to subtract.
        @return instance of class Waveform with other subtracted from self
        @note does not affect self
        @note
        valid types of other to subtract are:

        - Waveform - if the other waveform has the same time descriptor, returns the waveform
        with self and others values subtracted, otherwise adapts other to self and then
        subtracts them.
        - float,int,complex - subtracts the constant value from all values in self.
        @throw SignalIntegrityExceptionWaveform if other cannot be subtracted.
        @see AdaptedWaveforms
        """
        if isinstance(other,Waveform):
            if self.td == other.td:
                return Waveform(self.td,self.values-other.values)
            else:
                [s,o]=AdaptedWaveforms([self,other])
                return Waveform(s.td,s.values-o.values)
        elif isinstance(other,(float,int,complex)):
            return Waveform(self.td,self.values-other.real)
        # pragma: silent exclude
        else:
            raise SignalIntegrityExceptionWaveform('cannot subtract type' + str(other.__class__.__name__) + ' from waveform')
        # pragma: include
    def __radd__(self, other):
        """radd version
        this is used for summing waveforms in a list and is required.
        @param other instance of class Waveform or float, int, complex to add.
        @return self+other
        @see Waveform.__add__()
        """
        if isinstance(other,int):
            if other == 0: return Waveform(self)
            else: return self.__add__(other)
        else: return self.__add__(other)
    def __mul__(self,other):
        """overloads *
        @param other instance of class WaveformProcessor or float, int, complex to multiply by.
        @return instance of class Waveform with other multiplied by self
        @note does not affect self
        @note Waveform multiplication is an abstraction in some cases. The result for types
        of other is:
        - FrequencyResponse - returns self convolved with the corresponding impulse response.
        - ImpulseResponse - returns self convolved with the impulse response.
        - WaveformProcessor - returns self processed by the instance of WaveformProcessor.
        - float,int,complex - returns the Waveform produced by multiplying all of the values in
        self multiplied by the constant value supplied.
        @note The most obvious type of WaveformProcessor is a FirFilter, but there are others like
        WaveformTrimmer and WaveformDecimator.
        @throw SignalIntegrityExceptionWaveform if other cannot be multiplied.
        """
        # pragma: silent exclude
        from SignalIntegrity.Lib.TimeDomain.Filters.WaveformProcessor import WaveformProcessor
        from SignalIntegrity.Lib.FrequencyDomain.FrequencyResponse import FrequencyResponse
        from SignalIntegrity.Lib.TimeDomain.Waveform.ImpulseResponse import ImpulseResponse
        # pragma: include
        if isinstance(other,FrequencyResponse):
            return self * other.ImpulseResponse()
        elif isinstance(other,ImpulseResponse):
            return self * other.FirFilter()
        if isinstance(other,WaveformProcessor):
            return other.ProcessWaveform(self)
        elif isinstance(other,(float,int,complex)):
            result=copy(self)
            result.values=result.values*other.real
            return result
        elif isinstance(other,Waveform):
            [s,o]=AdaptedWaveforms([self,other])
            return Waveform(s.td,s.values*o.values)
        # pragma: silent exclude
        else:
            raise SignalIntegrityExceptionWaveform('cannot multiply waveform by type '+str(other.__class__.__name__))
        # pragma: include
    def __div__(self,other):
        return self.__truediv__(other)
    def __truediv__(self,other):
        """overloads /
        @param other instance of float, int, complex to divide by.
        @return instance of class Waveform with other divided into it.
        @note only handles float, int, complex where the constant values are divided into the
        values in self.
        @note should consider allowing a two waveforms to be divided, but frankly never came
        upon the need for that.
        @throw SignalIntegrityExceptionWaveform if other cannot be multiplied.
        """
        if isinstance(other,(float,int,complex)):
            return Waveform(self.td,self.values/other.real)
        # pragma: silent exclude
        else:
            raise SignalIntegrityExceptionWaveform('cannot divide waveform by type '+str(other.__class__.__name__))
        # pragma: include
    def ReadFromFile(self,fileName):
        """reads a waveform from a file
        @param fileName string name of file to read
        @return self
        @note this DOES affect self
        @note the normal waveform format is one number per line starting with the
        horizontal offset followed by the number of points followed by the sample
        rate.  The remaining lines contain one waveform point per line.  This is
        the format output by SignalIntegrity.  However, if the data is all on one line, then
        the format is assumed to be LeCroy MathPack format with the first point
        being the number of points, and the remaining points being time and value.
        @note if the file extension is '.trc', then LeCroy waveform format is assumed
        """
        # pragma: silent exclude
        _, file_extension = os.path.splitext(fileName)
        if file_extension == '.trc':
            self.ReadLeCroyWaveform(fileName)
            return self
        try:
        # pragma: include outdent
            with open(fileName,'rU' if sys.version_info.major < 3 else 'r') as f:
                data=f.readlines()
                # pragma: silent exclude
                if len(data)==1:
                    data=data[0].split()
                    NumPts=int(float(data[0])+0.5)
                    HorOffset=float(data[1])
                    SampleRate=1./(float(data[3])-HorOffset)
                    Values=[float(data[k*2+2]) for k in range(NumPts)]
                else:
                    # pragma: silent include outdent
                    HorOffset=float(data[0])
                    NumPts=int(float(data[1])+0.5)
                    SampleRate=float(data[2])
                    Values=[float(data[k+3]) for k in range(NumPts)]
                    # pragma: silent indent
            self.td=TimeDescriptor(HorOffset,NumPts,SampleRate)
            self.values=Waveform._coerce(Values)
        # pragma: silent exclude indent
        except IOError:
            raise SignalIntegrityExceptionWaveformFile(fileName+' not found')
        # pragma: include
        return self
    def WriteToFile(self,fileName):
        """writes a waveform to a file
        @param fileName string name of file to write
        @return self
        @note the waveform format written is one number per line starting with the
        horizontal offset followed by the number of points followed by the sample
        rate.  The remaining lines contain one waveform point per line.
        """
        # pragma: silent exclude
        _, file_extension = os.path.splitext(fileName)
        if file_extension == '.trc':
            self.WriteLeCroyWaveform(fileName)
            return self
        if file_extension == '.csv':
            self.WriteCsvWaveform(fileName)
            return self
        # pragma: include
        with open(fileName,"w") as f:
            td=self.td
            f.write(str(td.H)+'\n')
            f.write(str(int(td.K))+'\n')
            f.write(str(td.Fs)+'\n')
            for v in self.values:
                f.write(str(v.item())+'\n')
        return self
    def __eq__(self,other):
        """overloads ==
        @param other instance of other waveform.
        @return boolean whether the waveforms are equal to each other.
        @note an epsilon of 1e-6 is used for the compare.
        """
        if other == None:
            return False
        if len(self) != len(other):
            return False
        if self.td != other.td:
            return False
        for k in range(len(self)):
            if abs(self[k]-other[k])>self.epsilon:
                return False
        return True
    def __ne__(self,other):
        """overloads !=
        @param other instance of other waveform.
        @return boolean whether the waveforms are not equal to each other.
        """
        return not self == other
    def Adapt(self,td):
        """adapts waveform to time descriptor  
        Waveform adaption is performed using upsampling, decimation, fractional delay,
        and waveform point trimming.
        @param td instance of class TimeDescriptor to adapt waveform to
        @return instance of class Waveform containing self adapted to the time descriptor
        @note does not affect self.
        @note the static member variable adaptionStrategy determines how to interpolate.  'SinX' means
        to use sinx/x interpolation, 'Linear' means to use linear interpolation.
        @see InterpolatorSinX
        @see SignalIntegrity.TimeDomain.Filters.InterpolatorSinX.FractionalDelayFilterSinX
        @see SignalIntegrity.TimeDomain.Filters.InterpolatorSinX.FractionalDelayFilterSinX
        @see SignalIntegrity.TimeDomain.Filters.InterpolatorLinear.InterpolatorLinear
        @see SignalIntegrity.TimeDomain.Filters.InterpolatorLinear.FractionalDelayFilterLinear
        @see SignalIntegrity.TimeDomain.Filters.WaveformTrimmer.WaveformTrimmer
        @see SignalIntegrity.TimeDomain.Filters.WaveformDecimator.WaveformDecimator
        @see SignalIntegrity.Rat.Rat
        """
        # pragma: silent exclude
        from SignalIntegrity.Lib.TimeDomain.Filters.InterpolatorSinX import InterpolatorSinX
        from SignalIntegrity.Lib.TimeDomain.Filters.InterpolatorSinX import FractionalDelayFilterSinX
        from SignalIntegrity.Lib.TimeDomain.Filters.InterpolatorLinear import InterpolatorLinear
        from SignalIntegrity.Lib.TimeDomain.Filters.InterpolatorLinear import FractionalDelayFilterLinear
        from SignalIntegrity.Lib.TimeDomain.Filters.WaveformTrimmer import WaveformTrimmer
        from SignalIntegrity.Lib.TimeDomain.Filters.WaveformDecimator import WaveformDecimator
        from SignalIntegrity.Lib.Rat import Rat
        # pragma: include
        wf=self
        (upsampleFactor,decimationFactor)=Rat(td.Fs/wf.td.Fs)
        if upsampleFactor>1:
            # pragma: silent exclude
            if wf.td.K*upsampleFactor > self.maximumWaveformSize:
                raise SignalIntegrityExceptionWaveform('waveform too large to process')
            # pragma: include
            wf=wf*(InterpolatorSinX(upsampleFactor) if wf.adaptionStrategy=='SinX'
                else InterpolatorLinear(upsampleFactor))
        ad=td/wf.td
        f=ad.D-int(math.floor(ad.D))
        if not ((f<self.epsilon) or ((1-f)<self.epsilon)):
            wf=wf*(FractionalDelayFilterSinX(f,True) if wf.adaptionStrategy=='SinX'
                else FractionalDelayFilterLinear(f,True))
            ad=td/wf.td
        if decimationFactor>1:
            decimationPhase=int(round(ad.TrimLeft())) % decimationFactor
            wf=wf*WaveformDecimator(decimationFactor,decimationPhase)
            ad=td/wf.td
        tr=WaveformTrimmer(max(0,int(round(ad.TrimLeft()))),
                           max(0,int(round(ad.TrimRight()))))
        wf=wf*tr
        return wf
    def Measure(self,time):
        """measures a value at a given time
        @param time float time to measure the value at.
        @return value at time specified
        @note will return None if time is not within the waveform
        @note linearly interpolates nearest point
        """
        sample=(time-self.td.H)*self.td.Fs
        k=int(math.floor(sample))
        if k < 0 or k > (self.td.K-1): return None
        frac=sample-k
        res=frac*(self[k+1]-self[k])+self[k]
        return res
    def FrequencyContent(self,fd=None):
        """frequency content  
        provides the frequency content equivalent of the waveform.
        @param fd (optional) instance of class FrequencyList providing
        frequencies to provide the content for (defaults to None)
        @return instance of class FrequencyContent containing the frequency content of the
        waveform.
        @note if None is supplied for fd, the frequency content is provided using the frequency
        list corresponding to the time descriptor inherent to the waveform.  In this way,
        self.FrequencyContent().Waveform() equals self.
        @see SignalIntegrity.FrequencyDomain.FrequencyContent
        @see SignalIntegrity.FrequencyDomain.FrequencyList
        """
        # pragma: silent exclude
        from SignalIntegrity.Lib.FrequencyDomain.FrequencyContent import FrequencyContent
        # pragma: include
        return FrequencyContent(self,fd)
    def SpectralDensity(self,fd=None):
        """spectral density
        provides the spectral density equivalent of the waveform.
        @param fd (optional) instance of class FrequencyList providing
        frequencies to provide the content for (defaults to None)
        @return instance of class SpectralDensity containing the spectral density of the
        waveform.
        @note if None is supplied for fd, the spectral density is provided using the frequency
        list corresponding to the time descriptor inherent to the waveform.  In this way,
        self.SpectralDensity().Waveform() equals self.
        @see SignalIntegrity.FrequencyDomain.SpectralDensity
        @see SignalIntegrity.FrequencyDomain.FrequencyList
        """
        # pragma: silent exclude
        from SignalIntegrity.Lib.FrequencyDomain.SpectralDensity import SpectralDensity
        # pragma: include
        return self.FrequencyContent().SpectralDensity().Resample(fd)
    def Integral(self,c=0.,addPoint=True,scale=True):
        """integral of waveform  
        the integral is calculated using Riemann sums (as opposed to trapezoidal
        integration.
        @param c (optional) float value to add to the integral waveform
        @param addPoint (optional) boolean whether to add a point to the waveform before
        the first point.  the value added is c.
        @param scale (optional) boolean whether to multiply each sum by the sample period
        providing a true integral.  Otherwise, the values are simply summed.
        """
        td=copy(self.td)
        T=1./td.Fs if scale else 1.
        i=np.cumsum(self.values*T)+c
        td.H=td.H+(1./2.)*(1./td.Fs)
        if addPoint:
            td.K=td.K+1
            td.H=td.H=td.H-1./td.Fs
            i=np.concatenate(([c],i))
        return Waveform(td,i)
    def Derivative(self,c=0.,removePoint=True,scale=True):
        """derivative of waveform  
        the derivative is calculated using the difference divided by the sample period.
        @param c (optional) this value is superfluous and not used.
        @param removePoint (optional) boolean whether to remove the first point.  If the
        first point is not removed, it is zero.
        @param scale (optional) boolean whether to divide each difference by the sample period
        providing a true derivative.  Otherwise, the values are simply subtracted.
        @todo remove argument c.
        """
        td=copy(self.td)
        T=1./td.Fs if scale else 1.
        vl=np.empty_like(self.values)
        if len(vl)>0:
            vl[0]=0.
            vl[1:]=np.diff(self.values)/T
        td.H=td.H-(1./2.)*(1./td.Fs)
        if removePoint:
            td.K=td.K-1
            td.H=td.H+1./td.Fs
            vl=vl[1:]
        return Waveform(td,vl)
    def WriteLeCroyWaveform(self,filename):
        """Save self waveform in lecroy trc format
        @param filename String name of the filename to save to.  Should have a .trc extension
        """
        to_trc(self,filename)
    def ReadLeCroyWaveform(self,filename):
        """Read a waveform in lecroy trc format into self
        @param filename String name of the filename to read.  Should have a .trc extension
        @return self
        """
        wf=from_trc(filename)
        self.__init__(wf)
        return self
    def WriteCsvWaveform(self,filename):
        """Write waveform in csv format
        @param filename String name of the filename to read.  Should have a .trc extension
        @return self
        """
        with open(filename,'wt') as f:
            f.writelines([f'{t} {v}\n' for t,v in zip(self.Times(),self.Values())])
        return self
    def rms(self):
        """root-mean-square of the waveform values
        @return float rms value
        """
        return np.sqrt(np.mean(np.square(self.values)))
    def dBm(self,P=1e-3,R=50):
        return 20*math.log10(self.rms())-10*math.log10(P*R)

class WaveformFileAmplitudeOnly(Waveform):
    def __init__(self,fileName,td=None):
        if not td is None:
            HorOffset=td.H
            NumPts=td.K
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
