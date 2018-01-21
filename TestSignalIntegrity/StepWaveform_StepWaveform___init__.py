class StepWaveform(Waveform):
    def __init__(self,td,Amplitude=1.,StartTime=0.):
        t=td.Times()
        x=[0 if t[k] < StartTime else Amplitude for k in range(td.K)]
        Waveform.__init__(self,td,x)