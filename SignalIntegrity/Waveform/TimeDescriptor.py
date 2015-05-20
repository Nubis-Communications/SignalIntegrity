from SignalIntegrity.Filters.FilterDescriptor import FilterDescriptor

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
        if self.H != other.H: return False
        if self.N != other.N: return False
        if self.Fs != other.Fs: return False
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
            NumPts=(self.N-F.S)*F.U,
            SampleRate=self.Fs*F.U)
        return self
    def __mul__(self,F):
        return ApplyFilter(self,F)
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
                DelaySamples=other.N-self.N/UpsampleFactor-(self.H-other.H)*other.Fs,
                StartupSamples=other.N-self.N/UpsampleFactor)
    def DelayBy(self,D):
        self.H=self.H+D
        return self
    def FrequencyList(self):
        from SignalIntegrity.SParameters.FrequencyList import EvenlySpacedFrequencyList
        K=self.N
        N=K/2
        Fe=self.Fs/2.
        return EvenlySpacedFrequencyList(Fe,N)
    def Intersection(self,other):
        return TimeDescriptor(
            HorOffset=max(self.H,other.H),
            NumPts=max(0,min(self.TimeOfPoint(self.N),other.TimeOfPoint(other.N))-max(self.H,other.H))*self.Fs,
            SampleRate=self.Fs)
