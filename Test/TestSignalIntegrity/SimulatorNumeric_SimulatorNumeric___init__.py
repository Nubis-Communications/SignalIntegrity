class SimulatorNumeric(Simulator,Numeric):
    def __init__(self,sd=None):
        Simulator.__init__(self,sd)
    def TransferMatrix(self,Z0=50.):
        self.Check()
        VE_o=array(self.VoltageExtractionMatrix(self.m_ol))
        SIPrime=array(self.SIPrime(Left=VE_o))
        sm=array(self.SourceToStimsPrimeMatrix(Z0=Z0))
        Result=[list(v) for v in list(VE_o.dot(SIPrime).dot(sm))]
        return Result
