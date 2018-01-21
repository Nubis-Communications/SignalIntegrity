class StepWaveform(Waveform):
    def __init__(self,td,Amplitude=1.,StartTime=0.):
        x=[0 if t < StartTime else Amplitude for t in td.Times()]
        Waveform.__init__(self,td,x)