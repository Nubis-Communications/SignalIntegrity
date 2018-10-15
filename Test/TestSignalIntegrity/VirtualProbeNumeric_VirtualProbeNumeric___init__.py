class VirtualProbeNumeric(VirtualProbe,Numeric):
    def __init__(self,sd=None):
        VirtualProbe.__init__(self,sd)
    def TransferMatrix(self):
        if self.m_D is None:
            D=matrix(identity(len(self.StimsPrime())))
        else:
            D=self.m_D
        VE_m=matrix(self.VoltageExtractionMatrix(self.m_ml))
        VE_o=matrix(self.VoltageExtractionMatrix(self.m_ol))
        SIPrime_m=matrix(self.SIPrime(Left=VE_m,Right=D))
        SIPrime_o=matrix(self.SIPrime(Left=VE_o,Right=D))
        Left=(VE_o*SIPrime_m*matrix(D))
        Result=(Left*self.Dagger(VE_m*SIPrime_o*matrix(D),Left=Left)).tolist()
        return Result
