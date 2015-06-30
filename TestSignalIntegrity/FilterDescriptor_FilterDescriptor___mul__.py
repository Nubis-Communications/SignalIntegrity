class FilterDescriptor(object):
    def __init__(self,UpsampleFactor,DelaySamples,StartupSamples):
        self.U = UpsampleFactor
        self.D = DelaySamples
        self.S = StartupSamples
    def __mul__(self,other):
        if isinstance(other,FilterDescriptor):
            return FilterDescriptor(
                UpsampleFactor=self.U*other.U,
                DelaySamples=float(self.U*self.D+other.D)/self.U,
                StartupSamples=float(self.U*self.S+other.S)/self.U)
...
