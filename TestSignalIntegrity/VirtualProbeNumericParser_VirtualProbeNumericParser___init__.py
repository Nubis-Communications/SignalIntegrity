class VirtualProbeNumericParser(VirtualProbeParser):
    def __init__(self, f=None, args=None):
        VirtualProbeParser.__init__(self, f, args)
        self.m_tm=None
    def TransferMatrices(self):
        self.SystemDescription()
        self.m_sd.CheckConnections()
        spc=self.m_spc
        result=[]
        for n in range(len(self.m_f)):
            for d in range(len(self.m_spc)):
                self.m_sd.AssignSParameters(spc[d][0],spc[d][1][n])
            tm=VirtualProbeNumeric(self.m_sd).TransferMatrix()
            result.append(tm)
        return TransferMatrices(self.m_f,result)