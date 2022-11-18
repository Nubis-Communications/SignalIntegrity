"""
 s-parameters of netlists
"""

# Copyright (c) 2021 Nubis Communications, Inc.
# Copyright (c) 2018-2020 Teledyne LeCroy, Inc.
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
from SignalIntegrity.Lib.Parsers.SParametersParser import SParametersParser
from SignalIntegrity.Lib.SParameters import SParameters
from SignalIntegrity.Lib.Exception import SignalIntegrityExceptionSParameters
from SignalIntegrity.Lib.CallBacker import CallBacker
from SignalIntegrity.Lib.ResultsCache import LinesCache
from SignalIntegrity.Lib.ImpedanceProfile.PeeledLaunches import PeeledLaunches

class SystemSParametersNumericParser(SystemDescriptionParser,CallBacker,LinesCache):
    """generates system s-parameters from a netlist"""
    def __init__(self,f=None,args=None,callback=None,cacheFileName=None,efl=None,
                 Z0=50.):
        """constructor  
        frequencies may be provided at construction time (or not for symbolic solutions).
        @param f (optional) list of frequencies
        @param args (optional) string arguments for the circuit.
        @param callback (optional) function taking one argument as a callback
        @param cacheFileName (optional) string name of file used to cache results
        @param efl (optional) instance of class FrequencyList containing the evenly space frequency list
        to use for resampling in cases where time-domain transformations are required
        @param Z0 float (optional, defaults to 50.) reference impedance for the calculation
        @remark Arguments are provided on a line as pairs of names and values separated by a space.
        The optional callback is used as described in the class CallBacker.
        """
        SystemDescriptionParser.__init__(self,f,args,Z0=Z0)
        self.sf = None
        self.efl = efl
        # pragma: silent exclude
        CallBacker.__init__(self,callback)
        LinesCache.__init__(self,'SParameters',cacheFileName)
        # pragma: include
    # pragma: silent exclude
    @staticmethod
    def loop(ranges,SD,spc,solvetype):
        result=[None for r in range(len(ranges))]
        for r in ranges:
            for d in range(len(spc)):
                if not spc[d][0] is None:
                    SD.AssignSParameters(spc[d][0],spc[d][1][r])
            result[r-ranges[0]]=(SystemSParametersNumeric(SD).SParameters(
                solvetype=solvetype))
        return ranges,result
    # pragma: include
    def SParameters(self,solvetype='block',multicore=False):
        """compute the s-parameters of the netlist.
        @param solvetype (optional) string how to solve it. (defaults to 'block').
        @param multicore (optional) whether to solve multi core (defaults to 'false')
        @return instance of class SParameters as the solution of the network.
        @remark valid solvetype strings are:
        - 'block' - use the block matrix solution method.
        - 'direct' - use the direct method.
        'block' is faster and preferred, but direct is provided as an alternative and
        for testing. (Previously, instances were found where the block method failed,
        but the direct method did not - but this possibility is thought to be impossible
        now.
        @remark multicore might be possible only on Python 3.7 and higher
        """
        # pragma: silent exclude
        if self.CheckCache():
            self.CallBack(100.0)
            return self.sf
        # pragma: include
        self.SystemDescription()
        self.m_sd.CheckConnections()
        spc=self.m_spc
        result=[None for _ in range(len(self.m_f))]
        # praga: silent exclude
        if multicore:
            try:
                import concurrent.futures
            except:
                multicore=False
        if multicore:
            numCores=2
            resultsPerCore=len(result)//numCores # nominal results produced per core
            residual=len(result)-resultsPerCore*numCores # how many extra points must be produced
            # all of the initial cores produce one more point, until extra points are taken care of
            resultsPerCore=[resultsPerCore + (1 if c < residual else 0) for c in range(numCores)]
            if sum(resultsPerCore) != len(result): # this is an error
                # the calculation failed to figure out how to produce all of the points
                multicore=False
            else:
                # create a range of frequencies for each core to produce
                ranges=[None for c in range(numCores)]
                i=0
                for c in range(numCores):
                    ranges[c]=range(i,i+resultsPerCore[c])
                    i+=resultsPerCore[c]
        if multicore:
            with concurrent.futures.ProcessPoolExecutor(max_workers=numCores) as executor:
                futures = {executor.submit(self.loop,ranges[c],self.m_sd,spc,solvetype): c for c in range(numCores)}
                c=0
                for future in concurrent.futures.as_completed(futures):
                    c+=1
                    ranges,res = future.result()
#                 results=[self.loop(ranges[c],self.m_sd,spc,solvetype) for c in range(numCores)]
#                 for ranges,res in results:
                    for r in ranges:
                        result[r]=res[r-ranges[0]]
                    if self.HasACallBack():
                        progress=c/numCores*100.0
                        if not self.CallBack(progress):
                            raise SignalIntegrityExceptionSParameters('calculation aborted')
        else:
            # pragma: include outdent
            for n in range(len(self.m_f)):
                for d in range(len(spc)):
                    if not spc[d][0] is None:
                        self.m_sd.AssignSParameters(spc[d][0],spc[d][1][n])
                result[n]=(SystemSParametersNumeric(self.m_sd).SParameters(
                    solvetype=solvetype))
                # pragma: silent exclude
                if self.HasACallBack():
                    progress=(n+1)/len(self.m_f)*100.0
                    if not self.CallBack(progress):
                        raise SignalIntegrityExceptionSParameters('calculation aborted')
                # pragma: include indent
        self.sf = SParameters(self.m_f, result)
        # pragma: silent exclude
        if hasattr(self, 'delayDict'):
            td=[self.delayDict[p+1] if p+1 in self.delayDict else 0.0 for p in range(self.sf.m_P)]
            self.sf=PeeledLaunches(self.sf,td,method='exact')
        self.sf = SParametersParser(self.sf,self.m_ul,self.efl)
        self.CacheResult(['sf'])
        # pragma: include
        return self.sf
