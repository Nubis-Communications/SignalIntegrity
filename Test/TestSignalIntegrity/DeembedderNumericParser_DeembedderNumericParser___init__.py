class DeembedderNumericParser(DeembedderParser,CallBacker,LinesCache):
    def __init__(self, f=None, args=None, callback=None, cacheFileName=None, Z0=50.):
        DeembedderParser.__init__(self, f, args, Z0=Z0)
        self.sf = None
    def Deembed(self,systemSParameters=None):
        self._ProcessLines()
        self.m_sd.CheckConnections()
        NumUnknowns=len(self.m_sd.UnknownNames())
        result=[[] for i in range(NumUnknowns)]
        systemSP=systemSParameters
        if systemSP is None:
            for d in range(len(self.m_spc)):
                if self.m_spc[d][0] == 'system': systemSP=self.m_spc[d][1]
        for n in range(len(self.m_f)):
            for d in range(len(self.m_spc)):
                if not self.m_spc[d][0] in ['system',None]:
                    self.m_sd.AssignSParameters(self.m_spc[d][0],self.m_spc[d][1][n])
            system = systemSP[n] if not systemSP is None else None
            unl=DeembedderNumeric(self.m_sd).CalculateUnknown(system)
            if NumUnknowns == 1: unl=[unl]
            for u in range(NumUnknowns): result[u].append(unl[u])
        self.sf=[SParametersParser(SParameters(self.m_f,r,Z0=self.m_Z0),self.m_ul)
                 for r in result]
        if len(self.sf)==1: self.sf=self.sf[0]
        return self.sf
