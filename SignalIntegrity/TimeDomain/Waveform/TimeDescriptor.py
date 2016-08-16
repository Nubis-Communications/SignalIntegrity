'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
from SignalIntegrity.TimeDomain.Filters.FilterDescriptor import FilterDescriptor
from SignalIntegrity.FrequencyDomain.FrequencyList import EvenlySpacedFrequencyList

class TimeDescriptor(object):
    def __init__(self,HorOffset,NumPts,SampleRate):
        self.H = HorOffset
        self.N = NumPts
        self.Fs=SampleRate
    def __len__(self):
        return self.N
    def __getitem__(self,item):
        return item/self.Fs+self.H
    def __eq__(self,other):
        if abs(self.Fs - other.Fs) > 1e-15: return False
        if abs(self.H - other.H) > .00001*1./self.Fs: return False
        if self.N != other.N: return False
        return True
    def __ne__(self,other):
        return not self == other
    def Times(self,unit=None):
        if unit==None:
            return [self[k] for k in range(len(self))]
        elif isinstance(unit,float):
            return [self[k]/unit for k in range(len(self))]
        elif unit=='ps':
            return [self[k]/1.e-12 for k in range(len(self))]
        elif unit=='ns':
            return [self[k]/1.e-9 for k in range(len(self))]
        elif unit =='us':
            return [self[k]/1.e-6 for k in range(len(self))]
        elif unit == 'ms':
            return [self[k]/1.e-3 for k in range(len(self))]
    def ApplyFilter(self,F):
        return TimeDescriptor(
            HorOffset=self.H+(F.S-F.D)/self.Fs,
            NumPts=int(max(0,(self.N-F.S)*F.U)),
            SampleRate=self.Fs*F.U)
    def __mul__(self,F):
        return self.ApplyFilter(F)
    def __div__(self,other):
        if isinstance(other,FilterDescriptor):
            return TimeDescriptor(
                HorOffset=self.H+other.U/self.Fs*(other.D-other.S),
                NumPts=self.N/other.U+other.S,
                SampleRate=self.Fs/other.U)
        elif isinstance(other,TimeDescriptor):
            UpsampleFactor=self.Fs/other.Fs
            return FilterDescriptor(
                UpsampleFactor,
                DelaySamples=other.N-self.N/UpsampleFactor-
                    (self.H-other.H)*other.Fs,
                StartupSamples=other.N-self.N/UpsampleFactor)
    def DelayBy(self,D):
        return TimeDescriptor(self.H+D,self.N,self.Fs)
    def FrequencyList(self):
        K=self.N
        N=K/2
        Fe=self.Fs/2.
        return EvenlySpacedFrequencyList(Fe,N)
    def Intersection(self,other):
        return TimeDescriptor(
            HorOffset=max(self.H,other.H),
            NumPts=max(0,min(self.TimeOfPoint(self.N),
                other.TimeOfPoint(other.N))-max(self.H,other.H))*self.Fs,
            SampleRate=self.Fs)
    def TimeOfPoint(self,k):
        return self.H+float(k)/self.Fs
    def Print(self):
        print 'HorOffset:  '+str(self.H)
        print 'NumPts:     '+str(self.N)
        print 'SampleRate: '+str(self.Fs)
