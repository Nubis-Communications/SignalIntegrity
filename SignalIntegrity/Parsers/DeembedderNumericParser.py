'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
from SignalIntegrity.Parsers.DeembedderParser import DeembedderParser
from SignalIntegrity.SystemDescriptions import DeembedderNumeric
from SignalIntegrity.SParameters import SParameters
from SignalIntegrity.PySIException import PySIExceptionDeembedder
from SignalIntegrity.CallBacker import CallBacker

class DeembedderNumericParser(DeembedderParser,CallBacker):
    def __init__(self, f=None, args=None, callback=None):
        DeembedderParser.__init__(self, f, args)
        # pragma: silent exclude
        CallBacker.__init__(self,callback)
        # pragma: include
    def Deembed(self,systemSParameters=None):
        self._ProcessLines()
        self.m_sd.CheckConnections()
        NumUnknowns=len(self.m_sd.UnknownNames())
        result=[[] for i in range(NumUnknowns)]
        for n in range(len(self.m_f)):
            system=None
            for d in range(len(self.m_spc)):
                if self.m_spc[d][0] == 'system':
                    system=self.m_spc[d][1][n]
                else:
                    self.m_sd.AssignSParameters(self.m_spc[d][0],
                        self.m_spc[d][1][n])
            if not systemSParameters is None:
                system=systemSParameters[n]
            unl=DeembedderNumeric(self.m_sd).CalculateUnknown(system)
            if NumUnknowns == 1: unl=[unl]
            for u in range(NumUnknowns):
                result[u].append(unl[u])
            # pragma: silent exclude
            if self.HasACallBack():
                progress = self.m_f[n]/self.m_f[-1]*100.0
                if not self.CallBack(progress):
                    raise PySIExceptionDeembedder('calculation aborted')
            # pragma: include
        sf=[SParameters(self.m_f,r) for r in result]
        if len(sf)==1:
            return sf[0]
        return sf
