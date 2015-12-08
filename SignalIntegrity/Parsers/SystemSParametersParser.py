from SignalIntegrity.SystemDescriptions import SystemSParametersNumeric
from SignalIntegrity.Parsers import SystemDescriptionParser
from SignalIntegrity.SParameters import SParameters
from SignalIntegrity.PySIException import PySIExceptionCheckConnections

class SystemSParametersNumericParser(SystemDescriptionParser):
    def __init__(self,f=None,args=None):
        SystemDescriptionParser.__init__(self,f,args)
    def SParameters(self):
        self.SystemDescription()
        self.m_sd.CheckConnections()
        spc=self.m_spc
        result = []
        for n in range(len(self.m_f)):
            for d in range(len(spc)):
                self.m_sd[self.m_sd.IndexOfDevice(spc[d][0])].SParameters=spc[d][1][n]
            result.append(SystemSParametersNumeric(self.m_sd).SParameters())
        sf = SParameters(self.m_f, result)
        return sf