class VirtualProbeNumeric(VirtualProbe,Numeric):
    def __init__(self,sd=None):
        VirtualProbe.__init__(self,sd)
    def TransferMatrix(self):
        if self.m_D is None:
            D=identity(len(self.StimsPrime()))
        else:
            D=self.m_D
        VE_m=array(self.VoltageExtractionMatrix(self.m_ml))
        VE_o=array(self.VoltageExtractionMatrix(self.m_ol))
        SIPrime_m=array(self.SIPrime(Left=VE_m,Right=D))
        SIPrime_o=array(self.SIPrime(Left=VE_o,Right=D))
        Left=VE_o.dot(SIPrime_m).dot(array(D))
        Result=Left.dot(self.Dagger(VE_m.dot(SIPrime_o).dot(array(D)),Left=Left))
        return Result
