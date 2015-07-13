from numpy import matrix
from numpy import identity

from Simulator import Simulator

class SimulatorNumeric(Simulator):
    def __init__(self,sd):
        Simulator.__init__(self,sd)
    def TransferMatrix(self):
        VE_o=matrix(self.VoltageExtractionMatrix(self.m_ol))
        SIPrime=matrix(self.SIPrime())
        sm=matrix(self.SourceToStimsPrimeMatrix())
        Result=(VE_o*SIPrime*sm).tolist()
        return Result