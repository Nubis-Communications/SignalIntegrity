"""
 deembedded s-parameters from netlists
"""
# Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
# Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
# All Rights Reserved.
#
# Explicit license in accompanying README.txt file.  If you don't have that file
# or do not agree to the terms in that file, then you are not licensed to use
# this material whatsoever.

from SignalIntegrity.Parsers.DeembedderParser import DeembedderParser
from SignalIntegrity.SystemDescriptions.DeembedderNumeric import DeembedderNumeric
from SignalIntegrity.SParameters.SParameters import SParameters
from SignalIntegrity.PySIException import PySIExceptionDeembedder
from SignalIntegrity.CallBacker import CallBacker
from SignalIntegrity.ResultsCache import LinesCache

class DeembedderNumericParser(DeembedderParser,CallBacker,LinesCache):
    """generates deembedd s-parameters from a netlist"""
    def __init__(self, f=None, args=None, callback=None, cacheFileName=None):
        """constructor

        frequencies may be provided at construction time (or not for symbolic solutions).

        @param f (optional) list of frequencies
        @param args (optional) string arguments for the circuit.
        @param callback (optional) function taking one argument as a callback
        @param cacheFileName (optional) string name of file used to cache results

        Arguments are provided on a line as pairs of names and values separated by a space.

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
        """computes deembedded s-parameters of a netlist.
        @param systemSParameters (optional) instance of class SParameters referring
        to the s-parameters of the system 
        @return instance of class SParameters of the unknown devices in the network.
        """
        # pragma: silent exclude
        if not self.sf is None:
            return self.sf
        if self.CheckCache():
            self.CallBack(100.0)
            return self.sf
        # pragma: include
        self._ProcessLines()
        self.m_sd.CheckConnections()
        NumUnknowns=len(self.m_sd.UnknownNames())
        result=[[] for i in range(NumUnknowns)]
        for n in range(len(self.m_f)):
            system=None
            for d in range(len(self.m_spc)):
                if self.m_spc[d][0] == 'system': system=self.m_spc[d][1][n]
                else: self.m_sd.AssignSParameters(self.m_spc[d][0],self.m_spc[d][1][n])
            if not systemSParameters is None: system=systemSParameters[n]
            unl=DeembedderNumeric(self.m_sd).CalculateUnknown(system)
            if NumUnknowns == 1: unl=[unl]
            for u in range(NumUnknowns): result[u].append(unl[u])
            # pragma: silent exclude
            if self.HasACallBack():
                progress = self.m_f[n]/self.m_f[-1]*100.0
                if not self.CallBack(progress):
                    raise PySIExceptionDeembedder('calculation aborted')
            # pragma: include
        self.sf=[SParameters(self.m_f,r) for r in result]
        if len(self.sf)==1: self.sf=self.sf[0]
        # pragma: silent exclude
        self.CacheResult()
        # pragma: include
        return self.sf
