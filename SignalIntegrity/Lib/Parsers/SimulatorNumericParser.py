"""
numeric simulations from netlists
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

from SignalIntegrity.Lib.Parsers.SimulatorParser import SimulatorParser
from SignalIntegrity.Lib.Parsers.ParallelCalculations import Solve
from SignalIntegrity.Lib.FrequencyDomain.TransferMatrices import TransferMatrices
from SignalIntegrity.Lib.Exception import SignalIntegrityExceptionSimulator
from SignalIntegrity.Lib.CallBacker import CallBacker
from SignalIntegrity.Lib.ResultsCache import LinesCache

class SimulatorNumericParser(SimulatorParser,CallBacker,LinesCache):
    """performs numeric simulations from netlists"""
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
        solve may be distributed across processor cores.  When False the calculation runs
        serially; when True it may run in parallel if the cost model deems it worthwhile.
        @remark Arguments are provided on a line as pairs of names and values separated by a space.  
        The optional callback is used as described in the class CallBacker.  
        The use of the cacheFileName is described in the class LineCache.
        """
        SimulatorParser.__init__(self, f, args, Z0=Z0)
        self.transferMatrices = None
        self.allowParallel = allowParallel
        # pragma: silent exclude
        CallBacker.__init__(self,callback)
        LinesCache.__init__(self,'TransferMatrices',cacheFileName)
        # pragma: include
    def TransferMatrices(self):
        """calculates transfer matrices for simulation  
        Simulation, insofar as this class is concerned means generating transfer matrices for
        processing waveforms with.
        @return instance of class TransferMatrices
        @remark TransferMatrices are used with a TransferMatricesProcessor to process waveforms for
        simulation.
        """
        # pragma: silent exclude
        if self.CheckCache():
            if hasattr(self.transferMatrices, 'callback'):
                self.CallBack(100.0)
                return self.transferMatrices
            else:
                self.transferMatrices = None
                self.m_sd = None
        # pragma: include
        self.SystemDescription()
        self.m_sd.CheckConnections()
        spc=self.m_spc
        callback=None
        # pragma: silent exclude
        if self.HasACallBack():
            callback=lambda progress: self.CallBack(progress)
        # pragma: include
        result=Solve(
            'simulator',self.m_sd,spc,len(self.m_f),self.m_Z0,
            callback=callback,
            abortException=SignalIntegrityExceptionSimulator('calculation aborted'),
            allowParallel=self.allowParallel)
        self.transferMatrices=TransferMatrices(self.m_f,result)
        # pragma: silent exclude
        self.CacheResult(['transferMatrices','m_sd'])
        # pragma: include
        return self.transferMatrices