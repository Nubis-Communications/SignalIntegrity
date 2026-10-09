class TimeDescriptor(object):
    def __init__(self,HorOffset,NumPts,SampleRate):
        self.H = HorOffset
        self.K = int(NumPts)
        self.Fs=SampleRate
...
    def __len__(self):
        return self.K
    def __getitem__(self,item):
        return item/self.Fs+self.H
...
    def Times(self,unit=None):
        times=np.arange(self.K)/self.Fs+self.H
        if unit==None:
            return times.tolist()
        elif isinstance(unit,float):
            return (times/unit).tolist()
        elif unit=='ps':
            return (times/1.e-12).tolist()
        elif unit=='ns':
            return (times/1.e-9).tolist()
        elif unit =='us':
            return (times/1.e-6).tolist()
        elif unit == 'ms':
            return (times/1.e-3).tolist()
    def ApplyFilter(self,F):
        return TimeDescriptor(
            HorOffset=self.H+(F.S-F.D)/self.Fs,
            NumPts=int(max(0,(self.K-F.S)*F.U)),
            SampleRate=self.Fs*F.U)
    def __mul__(self,F):
        return self.ApplyFilter(F)
    def __div__(self,other):
        return self.__truediv__(other)
    def __truediv__(self,other):
        if isinstance(other,FilterDescriptor):
            return TimeDescriptor(
                HorOffset=self.H+other.U/self.Fs*(other.D-other.S),
                NumPts=self.K/other.U+other.S,
                SampleRate=self.Fs/other.U)
        elif isinstance(other,TimeDescriptor):
            UpsampleFactor=self.Fs/other.Fs
            return FilterDescriptor(
                UpsampleFactor,
                DelaySamples=other.K-self.K/UpsampleFactor-
                    (self.H-other.H)*other.Fs,
                StartupSamples=other.K-self.K/UpsampleFactor)
    def DelayBy(self,D):
        return TimeDescriptor(self.H+D,self.K,self.Fs)
    def FrequencyList(self):
        K=int(self.K)
        N=K//2
        Fe=float(self.Fs)*N/K
        return EvenlySpacedFrequencyList(Fe,N)
...
    def TimeOfPoint(self,k):
        return self.H+float(k)/self.Fs
...
