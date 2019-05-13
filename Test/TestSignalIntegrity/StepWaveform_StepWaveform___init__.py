class StepWaveform(Waveform):
    def __init__(self,td,Amplitude=1.,StartTime=0.,risetime=0.):
        x=[0 if t < StartTime else Amplitude for t in td.Times()]
        T=max(risetime/self.rtvsT,1/td.Fs)
        rcStart=max(0,td.IndexOfTime(StartTime-T/2.))
        if td.TimeOfPoint(rcStart)<StartTime-T/2: rcStart=min(rcStart+1,len(td)-1)
        rcEnd=min(len(td)-1,td.IndexOfTime(StartTime+T/2.))
        if td.TimeOfPoint(rcEnd)>StartTime+T/2: rcEnd=max(rcEnd-1,0)
        for i in range(rcStart,rcEnd):
            x[i]=Amplitude*(math.sin((td.TimeOfPoint(i)-StartTime)/T*math.pi)+1.)/2.
        Waveform.__init__(self,td,x)