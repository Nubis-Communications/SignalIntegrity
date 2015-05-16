class FilterDescriptor(object):
    def __init__(self,UpsampleFactor,DelaySamples,StartupSamples):
        self.U = UpsampleFactor
        self.D = DelaySamples
        self.S = StartupSamples
    def __mul__(self,other):
        if isinstance(other,FilterDescriptor):
            return FilterDescriptor(
                UpsampleFactor=self.U*other.U,
                DelaySamples=(self.U*self.D+other.D)/self.U,
                StartupSamples=(self.U*self.S+other.S)/self.U)
    def TrimLeft(self):
        return self.S-self.D
    def TrimRight(self):
        return self.D
    def TrimTotal(self):
        return self.S

class WaveformTrimmer(FilterDescriptor):
    def __init__(self,TrimLeft,TrimRight):
        FilterDescriptor.__init__(self,1,TrimRight,TrimLeft+TrimRight)