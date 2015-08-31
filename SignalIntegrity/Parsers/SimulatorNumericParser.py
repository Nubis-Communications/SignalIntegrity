from SimulatorParser import SimulatorParser
from SignalIntegrity.SystemDescriptions import SimulatorNumeric
from SignalIntegrity.FrequencyDomain.TransferMatrices import TransferMatrices
from SignalIntegrity.PySIException import PySIException

class SimulatorNumericParser(SimulatorParser):
    def __init__(self, f=None, args=None):
        SimulatorParser.__init__(self, f, args)
    def TransferMatrices(self):
        self.SystemDescription()
        if not self.m_sd.CheckConnections():
            raise PySIException('CheckConnections')
        spc=self.m_spc
        result=[]
        for n in range(len(self.m_f)):
            for d in range(len(self.m_spc)):
                self.m_sd[self.m_sd.IndexOfDevice(spc[d][0])].pSParameters=spc[d][1][n]
            tm=SimulatorNumeric(self.m_sd).TransferMatrix()
            result.append(tm)
        return TransferMatrices(self.m_f,result)