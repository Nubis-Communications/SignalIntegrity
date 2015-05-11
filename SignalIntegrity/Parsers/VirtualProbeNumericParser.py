from VirtualProbeParser import VirtualProbeParser
from SignalIntegrity.SystemDescriptions import VirtualProbeNumeric
from SignalIntegrity.SParameters import SParameters
from SignalIntegrity.SParameters import FrequencyResponse
from SignalIntegrity.SParameters import ImpulseResponse

class VirtualProbeNumericParser(VirtualProbeParser):
    def __init__(self, f=None, args=None):
        VirtualProbeParser.__init__(self, f, args)
        self.m_tm=None
    def TransferMatrices(self):
        if not self.m_tm == None:
            return self.m_tm
        self.SystemDescription()
        if not self.m_sd.CheckConnections():
            return
        spc=self.m_spc
        result=[]
        for n in range(len(self.m_f)):
            for d in range(len(self.m_spc)):
                self.m_sd[self.m_sd.IndexOfDevice(spc[d][0])].pSParameters=spc[d][1][n]
            result.append(VirtualProbeNumeric(self.m_sd).TransferMatrix())
        self.m_tm=SParameters(self.m_f,result)
        return self.m_tm
    def FrequencyResponses(self):
        tm = self.TransferMatrices()
        ml = self.SystemDescription().pMeasurementList
        ol = self.SystemDescription().pOutputList
        return [[FrequencyResponse(self.m_f,tm.Response(o,m))
            for m in range(len(ml))] for o in range(len(ol))]
    def ImpulseResponses(self):
        fr = self.FrequencyResponses()
        ml = self.SystemDescription().pMeasurementList
        ol = self.SystemDescription().pOutputList
        return [[fr[o][m].ImpulseResponse()
            for m in range(len(ml))] for o in range(len(ol))]