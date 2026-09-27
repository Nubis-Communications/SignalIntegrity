class FilterDescriptor(object):
...
    def Before(self,other):
        return FilterDescriptor(
                UpsampleFactor=self.U,
                DelaySamples=(other.D*other.U+self.D)/other.U-other.D/self.U,
                StartupSamples=(other.U*other.S+self.S)/other.U-other.S/self.U)
    def After(self,other):
        return FilterDescriptor(
                UpsampleFactor=self.U,
                DelaySamples=(self.D*self.U+other.D)*other.U/self.U-other.D*other.U,
                StartupSamples=(self.S*self.U+other.S)*other.U/self.U-other.U*other.S)
...
