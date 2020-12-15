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
from SignalIntegrity.Lib.TimeDomain.Waveform.Waveform import Waveform

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
    def ProcessWaveforms(self,wfl,td=None,adaptToLargest=False):
        """processes input waveforms and produces output waveforms
        @param wfl list of Waveform input waveforms to process.  If numbers are in the
        waveform list, they are assumed to be DC waveforms, that are treated specially.
        @param td (optional) instance of class TimeDescriptor.  If this is included,
        all final waveforms are adapted to this descriptor.  Otherwise, the sample rates of
        each waveform are used in the computation of the impulse responses.
        @param adaptToLargest bool (optional, defaults to False) causes waveform adaption
        during summation to choose the waveform with the largest absolute value of a point.
        This helps when models have frequency responses near the end frequency and causes
        the adaption to resample the smaller waveforms, which have less effect.
        @remark Externally, the order of the input and output waveforms are known.  The
        input waveforms must be provided in that order and the output waveforms are
        produced in that order.
        """
        if td is None:
            td = [wflm.td.Fs if isinstance(wflm,Waveform) else None for wflm in wfl]
        ir = self.TransferMatrices.ImpulseResponses(td)
        fr = self.TransferMatrices.FrequencyResponses() # for DC inputs
        result=[]
        for o in range(len(ir)):
            acc=[]
            for i in range(len(ir[o])):
                acc.append(ir[o][i].FirFilter().FilterWaveform(wfl[i])
                           if isinstance(wfl[i],Waveform)
                           else (wfl[i]*fr[o][i][0]).real)
                # pragma: silent exclude
                if self.HasACallBack():
                    progress=(float(o)/len(ir)+float(i)/(len(ir)*len(ir[o])))*100.0
                    if not self.CallBack(progress):
                        raise SignalIntegrityExceptionSimulator('calculation aborted')
            if adaptToLargest and len(acc)>1:
                largestValue=0.0; largestIndex=0
                for wfi in range(len(acc)):
                    if isinstance(acc[wfi],Waveform):
                        absMax=max(acc[wfi].Values('abs'))
                        if absMax>=largestValue:
                            largestIndex=wfi; largestValue=absMax
                acc=[acc[largestIndex]]+acc[0:largestIndex]+acc[largestIndex+1:]
            # if the first element of the accumulator is not a waveform (a number, assuming a DC value),
            # then rearrange so a waveform comes first.
            if not isinstance(acc[0],Waveform):
                for wfi in range(len(acc)):
                    if isinstance(acc[wfi],Waveform):
                        acc=[acc[wfi]]+acc[0:wfi]+acc[wfi+1:]
                        break
                # pragma: include
            result.append(sum(acc))
        return result
