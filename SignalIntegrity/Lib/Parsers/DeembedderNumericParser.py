"""
 deembedded s-parameters from netlists
"""
# Copyright (c) 2018-2020 Teledyne LeCroy, Inc.
# Copyright (c) 2021-2025 Nubis Communications, Inc.
# Copyright (c) 2026 Ciena, Inc.
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
from SignalIntegrity.Lib.Parsers.ParallelCalculations import Solve
from SignalIntegrity.Lib.SParameters.SParameters import SParameters
from SignalIntegrity.Lib.Exception import SignalIntegrityExceptionDeembedder
from SignalIntegrity.Lib.CallBacker import CallBacker
from SignalIntegrity.Lib.ResultsCache import LinesCache
from SignalIntegrity.Lib.ImpedanceProfile.PeeledLaunches import PeeledLaunches

class DeembedderNumericParser(DeembedderParser,CallBacker,LinesCache):
    """generates deembedd s-parameters from a netlist"""
    def __init__(self, f=None, args=None, callback=None, cacheFileName=None, Z0=50.,
                 allowParallel=False):
        """constructor  
        frequencies may be provided at construction time (or not for symbolic solutions).
        @param f (optional) list of frequencies
        @param args (optional) string arguments for the circuit.
        @param callback (optional) function taking one argument as a callback
        @param cacheFileName (optional) string name of file used to cache results
        @param Z0 float (optional, defaults to 50.) reference impedance for the calculation
        @param allowParallel bool (optional, defaults to False) whether the per-frequency
        deembedding solve may be distributed across processor cores.  When False the
        calculation runs serially; when True it may run in parallel if the cost model
        deems it worthwhile.
        @remark Arguments are provided on a line as pairs of names and values separated by a space.  
        The optional callback is used as described in the class CallBacker.  
        The use of the cacheFileName is described in the class LineCache
        """
        DeembedderParser.__init__(self, f, args, Z0=Z0)
        self.sf = None
        self.allowParallel = allowParallel
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
        # pragma: silent exclude
        if self.HasACallBack():
            callback=lambda progress: self.CallBack(progress)
        # pragma: include
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
        # pragma: silent exclude
        self.CacheResult(['sf','m_sd'])
        # pragma: include
        return self.sf
