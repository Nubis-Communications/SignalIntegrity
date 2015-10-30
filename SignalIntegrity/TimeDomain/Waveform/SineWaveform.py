import math

from SignalIntegrity.TimeDomain.Waveform.Waveform import Waveform

class SineWaveform(Waveform):
    def __init__(self,td,Amplitude=1.,Frequency=1e6,Phase=0.):
        times=td.Times()
        x=[Amplitude*math.sin(2.*math.pi*Frequency*t+Phase/2./math.pi) for t in times]
        Waveform.__init__(self,td,x)