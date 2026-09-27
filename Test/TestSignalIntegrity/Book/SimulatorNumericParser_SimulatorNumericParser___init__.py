class SimulatorNumericParser(SimulatorParser,CallBacker,LinesCache):
    def __init__(self, f=None, args=None, callback=None, cacheFileName=None, Z0=50.,
                 allowParallel=False):
        SimulatorParser.__init__(self, f, args, Z0=Z0)
        self.transferMatrices = None
        self.allowParallel = allowParallel
    def TransferMatrices(self):
        self.SystemDescription()
        self.m_sd.CheckConnections()
        spc=self.m_spc
        callback=None
        result=Solve(
            'simulator',self.m_sd,spc,len(self.m_f),self.m_Z0,
            callback=callback,
            abortException=SignalIntegrityExceptionSimulator('calculation aborted'),
            allowParallel=self.allowParallel)
        self.transferMatrices=TransferMatrices(self.m_f,result)
        return self.transferMatrices