class DeembedderParser(SystemDescriptionParser):
    def __init__(self, f=None, args=None, Z0=50.):
        SystemDescriptionParser.__init__(self, f, args, Z0)
    def _ProcessDeembedderLine(self,line):
        lineList=self.ReplaceArgs(line.split())
        if len(lineList) == 0: return
        if lineList[0] == 'system':
            dev=DeviceParser(self.m_f,None,None,lineList[1:],Z0=self.m_Z0)
            if not dev.m_spf is None:
                self.m_spc.append(('system',dev.m_spf))
        elif lineList[0] == 'unknown':
            self.m_sd.AddUnknown(lineList[1],int(lineList[2]))
        else: self.m_ul.append(line)
    def _ProcessLines(self):
        SystemDescriptionParser._ProcessLines(self,['connect','port'])
        self.m_sd = Deembedder(self.m_sd)
        lines=copy.deepcopy(self.m_ul); self.m_ul=[]
        for line in lines: self._ProcessDeembedderLine(line)
        lines=copy.deepcopy(self.m_ul); self.m_ul=[]
        for line in lines: SystemDescriptionParser._ProcessLine(self,line,[])
        return self
