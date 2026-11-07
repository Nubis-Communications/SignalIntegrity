class SimulatorNumeric(Simulator,Numeric):
    def __init__(self,sd=None):
        Simulator.__init__(self,sd)
    def TransferMatrix(self,Z0=50.):
        self.Check()
        if not hasattr(self, 'VE_o'):
            self.VE_o=array(self.VoltageExtractionMatrix(self.m_ol))
            self.sm=array(self.SourceToStimsPrimeMatrix(Z0=Z0))
        SIPrime=array(self.SIPrime(Left=self.VE_o))
        Result=[list(v) for v in list(self.VE_o.dot(SIPrime).dot(self.sm))]
        return Result
