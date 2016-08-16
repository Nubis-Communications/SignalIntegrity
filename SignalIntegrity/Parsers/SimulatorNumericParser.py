'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
from SimulatorParser import SimulatorParser
from SignalIntegrity.SystemDescriptions import SimulatorNumeric
from SignalIntegrity.FrequencyDomain.TransferMatrices import TransferMatrices
from SignalIntegrity.PySIException import PySIExceptionSimulator
from SignalIntegrity.CallBacker import CallBacker

class SimulatorNumericParser(SimulatorParser,CallBacker):
    def __init__(self, f=None, args=None,  callback=None):
        SimulatorParser.__init__(self, f, args)
        # pragma: silent exclude
        CallBacker.__init__(self,callback)
        # pragma: include
    def TransferMatrices(self):
        self.SystemDescription()
        self.m_sd.CheckConnections()
        spc=self.m_spc
        result=[]
        for n in range(len(self.m_f)):
            for d in range(len(self.m_spc)):
                self.m_sd.AssignSParameters(spc[d][0],spc[d][1][n])
            tm=SimulatorNumeric(self.m_sd).TransferMatrix()
            result.append(tm)
            # pragma: silent exclude
            if self.HasACallBack():
                progress = self.m_f[n]/self.m_f[-1]*100.0
                if not self.CallBack(progress):
                    raise PySIExceptionSimulator('calculation aborted')
            # pragma: include
        return TransferMatrices(self.m_f,result)