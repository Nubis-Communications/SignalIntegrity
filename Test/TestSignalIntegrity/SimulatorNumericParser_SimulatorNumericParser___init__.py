class SimulatorNumericParser(SimulatorParser,CallBacker,LinesCache):
    def __init__(self, f=None, args=None,  callback=None, cacheFileName=None, Z0=50.):
        SimulatorParser.__init__(self, f, args, Z0=Z0)
        self.transferMatrices = None
    def TransferMatrices(self):
        self.SystemDescription()
        self.m_sd.CheckConnections()
        spc=self.m_spc
        result=[]
        for n in range(len(self.m_f)):
            for d in range(len(self.m_spc)):
                if not spc[d][0] is None:
                    self.m_sd.AssignSParameters(spc[d][0],spc[d][1][n])
            tm=SimulatorNumeric(self.m_sd).TransferMatrix(Z0=self.m_Z0)
            result.append(tm)
        self.transferMatrices=TransferMatrices(self.m_f,result)
        return self.transferMatrices