'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
from SignalIntegrity.SystemDescriptions import SystemSParametersNumeric
from SignalIntegrity.Parsers.SystemDescriptionParser import SystemDescriptionParser
from SignalIntegrity.SParameters import SParameters
from SignalIntegrity.PySIException import PySIExceptionSParameters
from SignalIntegrity.CallBacker import CallBacker

class SystemSParametersNumericParser(SystemDescriptionParser,CallBacker):
    def __init__(self,f=None,args=None,callback=None):
        SystemDescriptionParser.__init__(self,f,args)
        # pragma: silent exclude
        CallBacker.__init__(self,callback)
        # pragma: include
    def SParameters(self):
        self.SystemDescription()
        self.m_sd.CheckConnections()
        spc=self.m_spc
        result = []
        for n in range(len(self.m_f)):
            for d in range(len(spc)):
                self.m_sd.AssignSParameters(spc[d][0],spc[d][1][n])
            result.append(SystemSParametersNumeric(self.m_sd).SParameters())
            # pragma: silent exclude
            if self.HasACallBack():
                progress=self.m_f[n]/self.m_f[-1]*100.0
                if not self.CallBack(progress):
                    raise PySIExceptionSParameters('calculation aborted')
            # pragma: include
        sf = SParameters(self.m_f, result)
        return sf