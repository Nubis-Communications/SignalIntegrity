from VirtualProbeParser import VirtualProbeParser
from SignalIntegrity.SystemDescriptions import VirtualProbeNumeric
from SignalIntegrity.SParameters import SParameters
from SignalIntegrity.SParameters import FrequencyResponse
from SignalIntegrity.SParameters import ImpulseResponse

from numpy import zeros

class VirtualProbeNumericParser(VirtualProbeParser):
    def __init__(self, f=None, args=None):
        VirtualProbeParser.__init__(self, f, args)
        self.m_tm=None
    def TransferMatrices(self,square=True):
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
            tm=VirtualProbeNumeric(self.m_sd).TransferMatrix()
            if square and not (len(tm)==len(tm[0])):
                P=max(len(tm),len(tm[0]))
                tme=zeros((P,P),complex).tolist()
                for r in range(len(tm)):
                    for c in range(len(tm[0])):
                        tme[r][c]=tm[r][c]
                tm=tme
            result.append(tm)
        self.m_tm=SParameters(self.m_f,result)
        return self.m_tm
    def FrequencyResponses(self):
        tm = self.TransferMatrices()
        ml = self.SystemDescription().pMeasurementList
        ol = self.SystemDescription().pOutputList
        return [[FrequencyResponse(self.m_f,tm.Response(o+1,m+1))
            for m in range(len(ml))] for o in range(len(ol))]
    def ImpulseResponses(self,td=None,**args):
        fr = self.FrequencyResponses()
        return [[fro_m.ImpulseResponse(td,**args) for fro_m in fro]
            for fro in fr]
    def ProcessWaveforms(self,wfl,td=None,**args):
        ir = self.ImpulseResponses(td,**args)
        return [sum([iro[m].FirFilter().FilterWaveform(wfl[m])
            for m in range(len(iro))]) for iro in ir]