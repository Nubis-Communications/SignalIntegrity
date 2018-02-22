# Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
# Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
# All Rights Reserved.
# 
# Explicit license in accompanying README.txt file.  If you don't have that file
# or do not agree to the terms in that file, then you are not licensed to use
# this material whatsoever.

from SignalIntegrity.PySIException import PySIExceptionSimulator
from SignalIntegrity.CallBacker import CallBacker

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
        all final waveforms are adapted to this descriptor.
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
                        raise PySIExceptionSimulator('calculation aborted')
                # pragma: include
            result.append(sum(acc))
        return result
