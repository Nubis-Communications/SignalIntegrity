from VirtualProbeParser import VirtualProbeParser
from SignalIntegrity.SystemDescriptions import VirtualProbeNumeric
from SignalIntegrity.SParameters import SParameters

class VirtualProbeNumericParser(VirtualProbeParser):
    def __init__(self, f=None, args=None):
        VirtualProbeParser.__init__(self, f, args)
    def TransferMatrices(self):
        self.SystemDescription()
        if not self.m_sd.CheckConnections():
            return
        spc=self.m_spc
        result=[]
        for n in range(len(self.m_f)):
            for d in range(len(self.m_spc)):
                self.m_sd[self.m_sd.IndexOfDevice(spc[d][0])].pSParameters=spc[d][1][n]
            result.append(VirtualProbeNumeric(self.m_sd).TransferMatrix())
        return SParameters(self.m_f,result)
