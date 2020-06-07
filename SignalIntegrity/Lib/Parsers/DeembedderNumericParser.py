"""
 deembedded s-parameters from netlists
"""

# Copyright (c) 2018 Teledyne LeCroy, Inc.
# All rights reserved worldwide.
#
# This file is part of SignalIntegrity.
#
# SignalIntegrity is free software: You can redistribute it and/or modify it under the terms
# of the GNU General Public License as published by the Free Software Foundation, either
# version 3 of the License, or any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <https://www.gnu.org/licenses/>

from SignalIntegrity.Lib.Parsers.DeembedderParser import DeembedderParser
from SignalIntegrity.Lib.Parsers.SParametersParser import SParametersParser
from SignalIntegrity.Lib.SystemDescriptions.DeembedderNumeric import DeembedderNumeric
from SignalIntegrity.Lib.SParameters.SParameters import SParameters
from SignalIntegrity.Lib.Exception import SignalIntegrityExceptionDeembedder
from SignalIntegrity.Lib.CallBacker import CallBacker
from SignalIntegrity.Lib.ResultsCache import LinesCache
from SignalIntegrity.Lib.ImpedanceProfile.PeeledLaunches import PeeledLaunches

class DeembedderNumericParser(DeembedderParser,CallBacker,LinesCache):
    """generates deembedd s-parameters from a netlist"""
    def __init__(self, f=None, args=None, callback=None, cacheFileName=None):
        """constructor  
        frequencies may be provided at construction time (or not for symbolic solutions).
        @param f (optional) list of frequencies
        @param args (optional) string arguments for the circuit.
        @param callback (optional) function taking one argument as a callback
        @param cacheFileName (optional) string name of file used to cache results
        @remark Arguments are provided on a line as pairs of names and values separated by a space.  
        The optional callback is used as described in the class CallBacker.  
        The use of the cacheFileName is described in the class LineCache
        """
        DeembedderParser.__init__(self, f, args)
        self.sf = None
        # pragma: silent exclude
        CallBacker.__init__(self,callback)
        LinesCache.__init__(self,'SParameters',cacheFileName)
        # pragma: include
    def Deembed(self,systemSParameters=None):
        """computes deembedded s-parameters of a netlist
        @param systemSParameters (optional) instance of class SParameters referring
        to the s-parameters of the system 
        @return instance of class SParameters of the unknown devices in the network.
        """
        # pragma: silent exclude
        if self.CheckCache():
            self.CallBack(100.0)
            return self.sf
        # pragma: include
        self._ProcessLines()
        self.m_sd.CheckConnections()
        NumUnknowns=len(self.m_sd.UnknownNames())
        result=[[] for i in range(NumUnknowns)]
        systemSP=systemSParameters
        if systemSP is None:
            for d in range(len(self.m_spc)):
                if self.m_spc[d][0] == 'system': systemSP=self.m_spc[d][1]
        # pragma: silent exclude
        if not systemSP is None:
            if hasattr(self, 'delayDict'):
                td=[self.delayDict[p+1] if p+1 in self.delayDict else 0.0 for p in range(systemSP.m_P)]
                systemSP=PeeledLaunches(systemSP,td,method='exact')
        # pragma: include
        for n in range(len(self.m_f)):
            for d in range(len(self.m_spc)):
                if not self.m_spc[d][0] in ['system',None]:
                    self.m_sd.AssignSParameters(self.m_spc[d][0],self.m_spc[d][1][n])
            system = systemSP[n] if not systemSP is None else None
            unl=DeembedderNumeric(self.m_sd).CalculateUnknown(system)
            if NumUnknowns == 1: unl=[unl]
            for u in range(NumUnknowns): result[u].append(unl[u])
            # pragma: silent exclude
            if self.HasACallBack():
                progress = self.m_f[n]/self.m_f[-1]*100.0
                if not self.CallBack(progress):
                    raise SignalIntegrityExceptionDeembedder('calculation aborted')
            # pragma: include
        self.sf=[SParametersParser(SParameters(self.m_f,r),self.m_ul) for r in result]
        if len(self.sf)==1: self.sf=self.sf[0]
        # pragma: silent exclude
        self.CacheResult()
        # pragma: include
        return self.sf
