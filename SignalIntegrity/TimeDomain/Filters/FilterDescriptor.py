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
    def TrimLeft(self):
        return self.S-self.D
    def TrimRight(self):
        return self.D
    def TrimTotal(self):
        return self.S
    def Print(self):
        print 'UpsampleFactor: '+str(self.U)
        print 'DelaySamples:   '+str(self.D)
        print 'StartupSamples: '+str(self.S)
        print 'TrimLeft:       '+str(self.TrimLeft())
        print 'TrimRight:      '+str(self.TrimRight())
        print 'TrimTotal:      '+str(self.TrimTotal())