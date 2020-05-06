class VirtualProbeNumericParser(VirtualProbeParser,CallBacker,LinesCache):
    def __init__(self, f=None, args=None, callback=None, cacheFileName=None):
        VirtualProbeParser.__init__(self, f, args)
        self.transferMatrices = None
        self.m_tm=None
    def TransferMatrices(self):
        self.SystemDescription()
        self.m_sd.CheckConnections()
        spc=self.m_spc
        result=[]
        for n in range(len(self.m_f)):
            for d in range(len(self.m_spc)):
                if not spc[d][0] is None:
                    self.m_sd.AssignSParameters(spc[d][0],spc[d][1][n])
            tm=VirtualProbeNumeric(self.m_sd).TransferMatrix()
            result.append(tm)
        self.transferMatrices=TransferMatrices(self.m_f,result)
        return self.transferMatrices