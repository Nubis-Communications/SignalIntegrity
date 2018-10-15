class SimulatorNumeric(Simulator,Numeric):
    def __init__(self,sd=None):
        Simulator.__init__(self,sd)
    def TransferMatrix(self):
        self.Check()
        VE_o=matrix(self.VoltageExtractionMatrix(self.m_ol))
        SIPrime=matrix(self.SIPrime(Left=VE_o))
        sm=matrix(self.SourceToStimsPrimeMatrix())
        Result=(VE_o*SIPrime*sm).tolist()
        return Result