class SystemSParametersNumericParser(SystemDescriptionParser,CallBacker,LinesCache):
    def __init__(self,f=None,args=None,callback=None,cacheFileName=None,efl=None,
                 Z0=50.,allowParallel=False):
        SystemDescriptionParser.__init__(self,f,args,Z0=Z0)
        self.sf = None
        self.efl = efl
        self.allowParallel = allowParallel
    def SParameters(self,solvetype='block'):
        self.SystemDescription()
        self.m_sd.CheckConnections()
        spc=self.m_spc
        callback=None
        result=Solve(
            'systemsparameters',self.m_sd,spc,len(self.m_f),self.m_Z0,
            callback=callback,
            abortException=SignalIntegrityExceptionSParameters('calculation aborted'),
            solvetype=solvetype,
            allowParallel=self.allowParallel)
        self.sf = SParameters(self.m_f, result,self.m_Z0)
        return self.sf