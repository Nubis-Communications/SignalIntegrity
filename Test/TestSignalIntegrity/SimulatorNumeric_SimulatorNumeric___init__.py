class SimulatorNumeric(Simulator,Numeric):
    def __init__(self,sd=None):
        Simulator.__init__(self,sd)
    def TransferMatrix(self):
        self.Check()
        VE_o=array(self.VoltageExtractionMatrix(self.m_ol))
        SIPrime=array(self.SIPrime(Left=VE_o))
        sm=array(self.SourceToStimsPrimeMatrix())
        Result=VE_o.dot(SIPrime).dot(sm)
        return Result
