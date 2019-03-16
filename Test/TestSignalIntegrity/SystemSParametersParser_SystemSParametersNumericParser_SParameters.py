class SystemSParametersNumericParser(SystemDescriptionParser,CallBacker,LinesCache):
    def __init__(self,f=None,args=None,callback=None,cacheFileName=None):
        SystemDescriptionParser.__init__(self,f,args)
        self.sf = None
    def SParameters(self,solvetype='block'):
        self.SystemDescription()
        self.m_sd.CheckConnections()
        spc=self.m_spc
        result = []
        for n in range(len(self.m_f)):
            for d in range(len(spc)):
                if not spc[d][0] is None:
                    self.m_sd.AssignSParameters(spc[d][0],spc[d][1][n])
            result.append(SystemSParametersNumeric(self.m_sd).SParameters(
                solvetype=solvetype))
        self.sf = SParameters(self.m_f, result)
        return self.sf