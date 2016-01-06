'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
class TransferMatricesProcessor(object):
    def __init__(self,transferMatrices):
        self.TransferMatrices=transferMatrices
    def ProcessWaveforms(self,wfl,td=None):
        if td is None:
            td = [wflm.TimeDescriptor().Fs for wflm in wfl]
        ir = self.TransferMatrices.ImpulseResponses(td)
        return [sum([iro[m].FirFilter().FilterWaveform(wfl[m])
            for m in range(len(iro))]) for iro in ir]