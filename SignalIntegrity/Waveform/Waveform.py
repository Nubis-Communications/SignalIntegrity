from TimeDescriptor import TimeDescriptor

class Waveform(object):
    def __init__(self,x=None,y=None):
        if isinstance(x,Waveform):
            self.m_t=x.m_t
            self.m_y=x.m_y
        elif isinstance(x,TimeDescriptor):
            self.m_t=x
            if isinstance(y,list):
                self.m_y=y
            else:
                self.m_y=[0 for k in range(x.N)]
        else:
            self.m_t=None
            self.m_y=None
    def __len__(self):
        return len(self.m_y)
    def __getitem__(self,item):
        return self.m_y[item]
    def Times(self,unit=None):
        return self.m_t.Times(unit)
    def TimeDescriptor(self):
        return self.m_t
    def Values(self):
        return self.m_y
    def OffsetBy(self,v):
        self.m_y = [y+v for y in self.m_y]
        return self
    def DelayBy(self,d):
        self.m_t.DelayBy(d)
        return self
    def __add__(self,other):
        if self.TimeDescriptor() == other.TimeDescriptor():
            return Waveform(self.TimeDescriptor(),[self[k]+other[k] for k in range(len(self))])
    def __sub__(self,other):
        if self.TimeDescriptor() == other.TimeDescriptor():
            return Waveform(self.TimeDescriptor(),[self[k]-other[k] for k in range(len(self))])

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
            NumpPts=len(wf)
        else:
            if len(wf) > NumPts:
                wf = [wf[k] for k in range(NumPts)]
            else:
                NumPts=len(wf)
        Waveform.__init__(self,TimeDescriptor(HorOffset,NumPts,SampleRate),wf)