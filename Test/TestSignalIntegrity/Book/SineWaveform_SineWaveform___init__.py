class SineWaveform(Waveform):
    def __init__(self,td,Amplitude=1.,Frequency=1e6,Phase=0.,
                 StartTime=-100.,StopTime=100.):
        times=np.asarray(td.Times())
        x=Amplitude*np.sin(2.*math.pi*Frequency*times+Phase/180.*math.pi)
        sw=Waveform(td,x)*PulseWaveform(td,Amplitude=1.,StartTime=StartTime,
            PulseWidth=max(StartTime,StopTime)-min(StartTime,StopTime),Risetime=0.)
        Waveform.__init__(self,sw.td,sw.Values())