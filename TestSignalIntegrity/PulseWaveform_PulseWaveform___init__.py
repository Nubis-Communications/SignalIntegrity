class PulseWaveform(Waveform):
    def __init__(self,td,Amplitude=1.,StartTime=0.,PulseWidth=0):
        StopTime=StartTime+PulseWidth
        t=td.Times()
        stepup=StepWaveform(td,Amplitude,StartTime)
        stepdown=StepWaveform(td,Amplitude,StopTime)
        Waveform.__init__(self,td,[stepup[k]-stepdown[k] for k in range(len(stepup))])