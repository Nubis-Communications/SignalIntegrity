class PulseWaveform(Waveform):
    def __init__(self,td,Amplitude=1.,StartTime=0.,PulseWidth=0.,Risetime=0.):
        StopTime=StartTime+PulseWidth
        stepup=StepWaveform(td,Amplitude,StartTime,Risetime)
        stepdown=StepWaveform(td,Amplitude,StopTime,Risetime)
        Waveform.__init__(self,td,[stepup[k]-stepdown[k] for k in range(len(stepup))])