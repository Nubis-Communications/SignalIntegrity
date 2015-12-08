from SignalIntegrity.Parsers import DeembedderParser
from SignalIntegrity.SystemDescriptions import DeembedderNumeric
from SignalIntegrity.SParameters import SParameters
from SignalIntegrity.PySIException import PySIExceptionCheckConnections

class DeembedderNumericParser(DeembedderParser):
    def __init__(self, f=None, args=None):
        DeembedderParser.__init__(self, f, args)
    def Deembed(self,systemSParameters=None):
        self._ProcessLines()
        self.m_sd.CheckConnections()
        result=[]
        for n in range(len(self.m_f)):
            system=None
            for d in range(len(self.m_spc)):
                if self.m_spc[d][0] == 'system':
                    system=self.m_spc[d][1][n]
                else:
                    self.m_sd[self.m_sd.IndexOfDevice(self.m_spc[d][0])].SParameters=\
                        self.m_spc[d][1][n]
            if not systemSParameters is None:
                system=systemSParameters[n]
            result.append(DeembedderNumeric(self.m_sd).CalculateUnknown(system))
        sf=SParameters(self.m_f,result)
        return sf
