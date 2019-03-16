"""
 s-parameters of netlists
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

from SignalIntegrity.Lib.SystemDescriptions.SystemSParametersNumeric import SystemSParametersNumeric
from SignalIntegrity.Lib.Parsers.SystemDescriptionParser import SystemDescriptionParser
from SignalIntegrity.Lib.SParameters import SParameters
from SignalIntegrity.Lib.Exception import SignalIntegrityExceptionSParameters
from SignalIntegrity.Lib.CallBacker import CallBacker
from SignalIntegrity.Lib.ResultsCache import LinesCache

class SystemSParametersNumericParser(SystemDescriptionParser,CallBacker,LinesCache):
    """generates system s-parameters from a netlist"""
    def __init__(self,f=None,args=None,callback=None,cacheFileName=None):
        """constructor

        frequencies may be provided at construction time (or not for symbolic solutions).

        @param f (optional) list of frequencies
        @param args (optional) string arguments for the circuit.
        @param callback (optional) function taking one argument as a callback
        @param cacheFileName (optional) string name of file used to cache results

        Arguments are provided on a line as pairs of names and values separated by a space.

        The optional callback is used as described in the class CallBacker.

        """
        SystemDescriptionParser.__init__(self,f,args)
        self.sf = None
        # pragma: silent exclude
        CallBacker.__init__(self,callback)
        LinesCache.__init__(self,'SParameters',cacheFileName)
        # pragma: include
    def SParameters(self,solvetype='block'):
        """compute the s-parameters of the netlist.
        @param solvetype (optional) string how to solve it. (defaults to 'block').
        @return instance of class SParameters as the solution of the network.
        valid solvetype strings are:
        - 'block' - use the block matrix solution method.
        - 'direct' - use the direct method.
        'block' is faster and preferred, but direct is provided as an alternative and
        for testing. (Previously, instances were found where the block method failed,
        but the direct method did not - but this possibility is thought to be impossible
        now.
        """
        # pragma: silent exclude
        if self.CheckCache():
            self.CallBack(100.0)
            return self.sf
        # pragma: include
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
            # pragma: silent exclude
            if self.HasACallBack():
                progress=self.m_f[n]/self.m_f[-1]*100.0
                if not self.CallBack(progress):
                    raise SignalIntegrityExceptionSParameters('calculation aborted')
            # pragma: include
        self.sf = SParameters(self.m_f, result)
        # pragma: silent exclude
        self.CacheResult()
        # pragma: include
        return self.sf