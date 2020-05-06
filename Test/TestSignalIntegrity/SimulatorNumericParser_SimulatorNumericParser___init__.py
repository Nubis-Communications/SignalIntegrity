class SimulatorNumericParser(SimulatorParser,CallBacker,LinesCache):
    def __init__(self, f=None, args=None,  callback=None, cacheFileName=None):
        SimulatorParser.__init__(self, f, args)
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
            tm=SimulatorNumeric(self.m_sd).TransferMatrix()
            result.append(tm)
        self.transferMatrices=TransferMatrices(self.m_f,result)
        return self.transferMatrices