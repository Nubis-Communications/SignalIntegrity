"""
TransferMatricesProcessor.py
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

from SignalIntegrity.Lib.Exception import SignalIntegrityExceptionSimulator
from SignalIntegrity.Lib.CallBacker import CallBacker

class TransferMatricesProcessor(CallBacker):
    """process transfer matrices

    Usually transfer matrices are produced in simulation and virtual probing
    solutions.  The resultant waveform processing for the final results are produced
    using this class.

    @see TransferMatrices"""
    def __init__(self,transferMatrices,callback=None):
        """Constructor
        @param transferMatrices instance of class TransferMatrices.
        @param callback (optional) reference to function that takes float percentage
        used for periodically calling to show progress and allow aborting.
        @see CallBacker
        """
        self.TransferMatrices=transferMatrices
        # pragma: silent exclude
        CallBacker.__init__(self,callback)
        # pragma: include
    def ProcessWaveforms(self,wfl,td=None):
        """processes input waveforms and produces output waveforms
        @param wfl list of Waveform input waveforms to process.
        @param td (optional) instance of class TimeDescriptor.  If this is included,
        all final waveforms are adapted to this descriptor.  Otherwise, the sample rates of
        each waveform are used in the computeation of the impulse responses.
        @remark
        Externally, the order of the input and output waveforms are known.  The
        input waveforms must be provided in that order and the output waveforms are
        produced in that order.
        """
        if td is None:
            td = [wflm.td.Fs for wflm in wfl]
        ir = self.TransferMatrices.ImpulseResponses(td)
        result=[]
        for o in range(len(ir)):
            acc=[]
            for i in range(len(ir[o])):
                acc.append(ir[o][i].FirFilter().FilterWaveform(wfl[i]))
                # pragma: silent exclude
                if self.HasACallBack():
                    progress=(float(o)/len(ir)+float(i)/(len(ir)*len(ir[o])))*100.0
                    if not self.CallBack(progress):
                        raise SignalIntegrityExceptionSimulator('calculation aborted')
                # pragma: include
            result.append(sum(acc))
        return result
