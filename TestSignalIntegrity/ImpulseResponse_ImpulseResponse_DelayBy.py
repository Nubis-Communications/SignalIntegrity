class ImpulseResponse(Waveform):
...
    def DelayBy(self,d):
        return ImpulseResponse(self.TimeDescriptor().DelayBy(d),self.Values())
...
    def _FractionalDelayTime(self):
        td=self.TimeDescriptor()
        TD=-(-td.H*td.Fs-math.floor(-td.H*td.Fs+0.5))/td.Fs
        return TD
...
