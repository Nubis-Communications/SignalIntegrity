class VirtualProbeNumericParser(VirtualProbeParser,CallBacker,LinesCache):
    def __init__(self, f=None, args=None, callback=None, cacheFileName=None, Z0=50.,
                 allowParallel=False):
        VirtualProbeParser.__init__(self, f, args, Z0=Z0)
        self.transferMatrices = None
        self.m_tm=None
        self.allowParallel = allowParallel
    def TransferMatrices(self):
        self.SystemDescription()
        self.m_sd.CheckConnections()
        spc=self.m_spc
        callback=None
        result=Solve(
            'virtualprobe',self.m_sd,spc,len(self.m_f),self.m_Z0,
            callback=callback,
            abortException=SignalIntegrityExceptionVirtualProbe('calculation aborted'),
            allowParallel=self.allowParallel)
        self.transferMatrices=TransferMatrices(self.m_f,result)
        return self.transferMatrices