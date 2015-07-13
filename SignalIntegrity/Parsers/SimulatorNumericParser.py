from SimulatorParser import SimulatorParser
from SignalIntegrity.SystemDescriptions import SimulatorNumeric
from SignalIntegrity.SParameters import SParameters
from SignalIntegrity.FrequencyDomain.FrequencyResponse import FrequencyResponse
from SignalIntegrity.TimeDomain.Waveform.ImpulseResponse import ImpulseResponse

from numpy import zeros

class TransferMatrixNumericProcessor(object):
    def __init__(self,className):
        self.m_className=className
        self.m_tm=None
    def TransferMatrices(self,square=True):
        if not self.m_tm == None:
            return self.m_tm
        self.SystemDescription()
        if not self.m_sd.CheckConnections():
            return # pragma: no cover
        spc=self.m_spc
        result=[]
        for n in range(len(self.m_f)):
            for d in range(len(self.m_spc)):
                self.m_sd[self.m_sd.IndexOfDevice(spc[d][0])].pSParameters=spc[d][1][n]
            tm=self.m_className(self.m_sd).TransferMatrix()
            self.m_inputs=len(tm[0])
            self.m_outputs=len(tm)
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
        return [[FrequencyResponse(self.m_f,tm.Response(o+1,s+1))
            for s in range(self.m_inputs)] for o in range(self.m_outputs)]
    def ImpulseResponses(self,td=None):
        fr = self.FrequencyResponses()
        if td is None or isinstance(td,float) or isinstance(td,int):
            td = [td for m in range(len(fr[0]))]
        return [[fro[m].ImpulseResponse(td[m]) for m in range(len(fro))]
            for fro in fr]
    def ProcessWaveforms(self,wfl,td=None):
        if td is None:
            td = [wflm.TimeDescriptor().Fs for wflm in wfl]
        ir = self.ImpulseResponses(td)
        return [sum([iro[m].FirFilter().FilterWaveform(wfl[m])
            for m in range(len(iro))]) for iro in ir]

class SimulatorNumericParser(SimulatorParser,TransferMatrixNumericProcessor):
    def __init__(self, f=None, args=None):
        SimulatorParser.__init__(self, f, args)
        TransferMatrixNumericProcessor.__init__(self,SimulatorNumeric)