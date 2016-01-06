'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
from numpy import matrix
from numpy import identity

from Simulator import Simulator

class SimulatorNumeric(Simulator):
    def __init__(self,sd=None):
        Simulator.__init__(self,sd)
    def TransferMatrix(self):
        self.Check()
        VE_o=matrix(self.VoltageExtractionMatrix(self.m_ol))
        SIPrime=matrix(self.SIPrime())
        sm=matrix(self.SourceToStimsPrimeMatrix())
        Result=(VE_o*SIPrime*sm).tolist()
        return Result