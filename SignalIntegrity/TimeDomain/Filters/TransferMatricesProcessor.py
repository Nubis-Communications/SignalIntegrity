'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
from SignalIntegrity.PySIException import PySIExceptionSimulator
from SignalIntegrity.CallBacker import CallBacker

class TransferMatricesProcessor(CallBacker):
    def __init__(self,transferMatrices,callback=None):
        self.TransferMatrices=transferMatrices
        # pragma: silent exclude
        CallBacker.__init__(self,callback)
        # pragma: include
    def ProcessWaveforms(self,wfl,td=None):
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
