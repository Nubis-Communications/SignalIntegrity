class DeembedderNumericParser(DeembedderParser,CallBacker,LinesCache):
    def __init__(self, f=None, args=None, callback=None, cacheFileName=None, Z0=50.,
                 allowParallel=False):
        DeembedderParser.__init__(self, f, args, Z0=Z0)
        self.sf = None
        self.allowParallel = allowParallel
    def Deembed(self,systemSParameters=None):
        self._ProcessLines()
        self.m_sd.CheckConnections()
        NumUnknowns=len(self.m_sd.UnknownNames())
        systemSP=systemSParameters
        if systemSP is None:
            for d in range(len(self.m_spc)):
                if self.m_spc[d][0] == 'system': systemSP=self.m_spc[d][1]
        # The per-frequency deembedding solves are independent, so they are
        # dispatched through the same parallel machinery used by the s-parameter
        # and simulator solves.  The 'system' device is excluded from the device
        # list handed to the solver (its per-frequency matrices are supplied
        # separately as systemMatrices); every other device (including None-named
        # internal connections) is assigned each frequency exactly as in the
        # original serial loop.
        spc=[self.m_spc[d] for d in range(len(self.m_spc))
             if self.m_spc[d][0] != 'system']
        systemMatrices=None
        if not systemSP is None:
            systemMatrices=[systemSP[n] for n in range(len(self.m_f))]
        callback=None
        perFrequency=Solve(
            'deembedder',self.m_sd,spc,len(self.m_f),self.m_Z0,
            callback=callback,
            abortException=SignalIntegrityExceptionDeembedder('calculation aborted'),
            allowParallel=self.allowParallel,
            systemMatrices=systemMatrices)
        result=[[] for i in range(NumUnknowns)]
        for n in range(len(self.m_f)):
            unl=perFrequency[n]
            if NumUnknowns == 1: unl=[unl]
            for u in range(NumUnknowns): result[u].append(unl[u])
        self.sf=[SParametersParser(SParameters(self.m_f,r,Z0=self.m_Z0),self.m_ul)
                 for r in result]
        if len(self.sf)==1: self.sf=self.sf[0]
        return self.sf
