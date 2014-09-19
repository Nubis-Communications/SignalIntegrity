from SignalIntegrity.SystemDescriptions import DeembedderNumeric
from SignalIntegrity.Parsers import SystemDescriptionParser
from SignalIntegrity.SParameterFiles import SParameters
from Devices.DeviceParser import DeviceParser
import copy

class DeembedderParser(SystemDescriptionParser):
    def __init__(self, f=None, args=None):
        SystemDescriptionParser.__init__(self, f, args)
    def _ProcessDeembedderLine(self,line):
        lineList=self.ReplaceArgs(line.split())
        if len(lineList) == 0:
            return
        if lineList[0] == 'system':
            dev=DeviceParser(self.m_f,[lineList[i] for i in range(1,len(lineList))])
            if not dev.m_spf is None:
                self.m_spc.append(('system',dev.m_spf))
        else:
            self.m_ul.append(line)
    def _ProcessLines(self):
        SystemDescriptionParser._ProcessLines(self)
        lines=copy.deepcopy(self.m_ul)
        self.m_ul=[]
        for line in lines:
            self._ProcessDeembedderLine(line)
        return self
