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
from SignalIntegrity.SParameters.SParameters import SParameters

class ShortStandard(SParameters):
    def __init__(self,f,offsetDelay=0.0,offsetZ0=50.0,offsetLoss=0.0,L0=0.0,L1=0.0,L2=0.0,L3=0.0):
        sd=SystemDescription()
        sd.AddDevice('offset',2)
        sd.AddDevice('L',1)
        sd.AddPort('offset',1,1)
        sd.ConnectDevicePort('offset',2,'L',1)
        sspn=SystemSParametersNumeric(sd)

        offsetSParameters=Offset(f,offsetDelay,offsetZ0,offsetLoss)
        terminationSParameters=TerminationLPolynomial(f,L0*1e-12,L1*1e-24,L2*1e-33,L3*1e-42)

        sp=[]
        for n in range(len(f)):
            sspn.AssignSParameters('offset',offsetSParameters[n])
            sspn.AssignSParameters('L',terminationSParameters[n])
            sp.append(sspn.SParameters())
        SParameters.__init__(self,f,sp)