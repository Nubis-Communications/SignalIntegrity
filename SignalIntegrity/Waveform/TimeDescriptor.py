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
    def Times(self):
        return [self[k] for k in range(len(self))]
    def ApplyFilter(self,F):
        return TimeDescriptor(
            HorOffset=self.H+(F.S-F.D)/self.Fs,
            NumPts=(self.N-F.S)*F.U,
            SampleRate=self.Fs*F.U)
        return self
    def __mul__(self,F):
        return ApplyFilter(self,F)
    def __div__(self,F):
        if isinstance(other,FilterDescriptor):
            return TimeDescriptor(
                HorOffset=self.H+F.U/self.Fs*(F.D-F.S),
                NumPts=self.N/F.U+F.S,
                SampleRate=self.Fs/F.U)
        elif isinstance(other,TimeDescriptor):
            UpsampleFactor=self.Fs/other.Fs
            return FilterDescriptor(
                UpsampleFactor,
                DelaySamples=other.N-self.N/UpsampleFactor-(self.H-other.H)*other.Fs,
                StartupSamples=other.N-self.N/UpsampleFactor)
    def DelayBy(self,D):
        self.H=self.H+D
        return self