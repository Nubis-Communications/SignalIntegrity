class StepWaveform(Waveform):
    def __init__(self,td,Amplitude=1.,StartTime=0.,risetime=0.):
        x=np.where(np.asarray(td.Times())<StartTime,0.,float(Amplitude))
        T=risetime/self.rtvsT
        rcStart=max(0,td.IndexOfTime(StartTime-T/2.))
        if td.TimeOfPoint(rcStart)<StartTime-T/2: rcStart=min(rcStart+1,len(td)-1)
        rcEnd=min(len(td)-1,td.IndexOfTime(StartTime+T/2.))
        if td.TimeOfPoint(rcEnd)>StartTime+T/2: rcEnd=max(rcEnd-1,0)
        if T != 0 and rcEnd >= rcStart:
            idx=np.arange(rcStart,rcEnd+1)
            tpts=td.H+idx/td.Fs
            x[idx]=Amplitude*(np.sin((tpts-StartTime)/T*math.pi)+1.)/2.
        Waveform.__init__(self,td,x)