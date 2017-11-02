'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''

from SignalIntegrity.SystemDescriptions.SystemDescription import SystemDescription
from SignalIntegrity.SystemDescriptions.SystemSParametersNumeric import SystemSParametersNumeric
from SignalIntegrity.Measurement.CalKit.Standards.TerminationPolynomial import TerminationLPolynomial
from SignalIntegrity.Measurement.CalKit.Standards.Offset import Offset

class ShortStandard(object):
    def __init__(self,f,offsetDelay=0.0,offsetZ0=50.0,offsetLoss,L0=0.0,L1=0.0,L2=0.0,L3=0.0):
        sd=SystemDescription()
        sd.AddDevice('offset',2)
        sd.AddDevice('L',1)
        sd.AddPort('offset',1,1)
        sd.ConnectDevicePort('offset',2,'L',1)
        sd.AssignSParameters('offset',Offset(f,offsetDelay,offsetZ0,offsetLoss))
        sd.AssignSParameters('L',TerminationLPolynomial(f,L0*1e-12,L1*1e-24,L2*1e-33,L3*1e-42))
        sspn=SystemSParametersNumeric(sd)
        self.sp=sspn.SParameters()
    def __getitem__(self,n):
        return self.sp[n][0][0]
