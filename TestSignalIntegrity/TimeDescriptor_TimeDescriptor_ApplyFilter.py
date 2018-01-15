class TimeDescriptor(object):
    def __init__(self,HorOffset,NumPts,SampleRate):
        self.H = HorOffset
        self.N = NumPts
        self.Fs=SampleRate
    def __len__(self):
        return self.N
    def __getitem__(self,item):
        return item/self.Fs+self.H
...
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
        K=int(self.N)
        N=K/2
        Fe=float(self.Fs)*N/K
        return EvenlySpacedFrequencyList(Fe,N)
...
    def TimeOfPoint(self,k):
        return self.H+float(k)/self.Fs
...
