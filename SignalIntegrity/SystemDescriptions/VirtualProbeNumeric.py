from numpy import matrix
from numpy import identity

from VirtualProbe import VirtualProbe

class VirtualProbeNumeric(VirtualProbe):
    def __init__(self,sd):
        VirtualProbe.__init__(self,sd)
    def TransferFunctions(self):
        if self.m_D is None:
            D=matrix(identity(len(self.StimsPrime())))
        else:
            D=self.m_D
        VE_m=matrix(self.VoltageExtractionMatrix(self.m_ml))
        VE_o=matrix(self.VoltageExtractionMatrix(self.m_ol))
        SIPrime=matrix(self.SIPrime())
        Result=(VE_o*SIPrime*matrix(D))*(VE_m*SIPrime*matrix(D)).getI()
        return Result
