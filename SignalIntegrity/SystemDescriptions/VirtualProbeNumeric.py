from numpy import matrix
from numpy import identity

from VirtualProbe import VirtualProbe
from SignalIntegrity.PySIException import PySIExceptionSimulator
from SignalIntegrity.PySIException import PySIExceptionVirtualProbe

class VirtualProbeNumeric(VirtualProbe):
    def __init__(self,sd=None):
        VirtualProbe.__init__(self,sd)
    def TransferMatrix(self):
        # pragma: silent exclude
        self.Check()
        # pragma: include
        if self.m_D is None:
            D=matrix(identity(len(self.StimsPrime())))
        else:
            D=self.m_D
        VE_m=matrix(self.VoltageExtractionMatrix(self.m_ml))
        VE_o=matrix(self.VoltageExtractionMatrix(self.m_ol))
        # pragma: silent exclude
        try:
        # pragma: include outdent
            SIPrime=matrix(self.SIPrime())
        # pragma: silent exclude indent
        except PySIExceptionSimulator as e:
            raise PySIExceptionVirtualProbe(e.message)
        # pragma: include
        Result=((VE_o*SIPrime*matrix(D))*(VE_m*SIPrime*matrix(D)).getI()).tolist()
        return Result
