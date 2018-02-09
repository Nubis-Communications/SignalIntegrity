class SineWaveform(Waveform):
    def __init__(self,td,Amplitude=1.,Frequency=1e6,Phase=0.):
        x=[Amplitude*math.sin(2.*math.pi*Frequency*t+Phase/180.*math.pi)
                for t in td.Times()]
        Waveform.__init__(self,td,x)