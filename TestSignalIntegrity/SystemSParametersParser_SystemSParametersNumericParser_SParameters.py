class SystemSParametersNumericParser(SystemDescriptionParser,CallBacker):
    def __init__(self,f=None,args=None,callback=None):
        SystemDescriptionParser.__init__(self,f,args)
    def SParameters(self,solvetype='block'):
        self.SystemDescription()
        self.m_sd.CheckConnections()
        spc=self.m_spc
        result = []
        for n in range(len(self.m_f)):
            for d in range(len(spc)):
                self.m_sd.AssignSParameters(spc[d][0],spc[d][1][n])
            result.append(SystemSParametersNumeric(self.m_sd).SParameters(
                solvetype=solvetype))
        sf = SParameters(self.m_f, result)
        return sf