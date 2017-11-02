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
from SignalIntegrity.SParameters.SParameters import SParameters
from SignalIntegrity.Measurement.CalKit.Standards.TerminationPolynomial import TerminationCPolynomial
from SignalIntegrity.Measurement.CalKit.Standards.Offset import Offset

class OpenStandard(SParameters):
    def __init__(self,f,offsetDelay=0.0,offsetZ0=50.0,offsetLoss=0.0,C0=0.0,C1=0.0,C2=0.0,C3=0.0):
        sd=SystemDescription()
        sd.AddDevice('offset',2)
        sd.AddDevice('C',1)
        sd.AddPort('offset',1,1)
        sd.ConnectDevicePort('offset',2,'C',1)
        sd.AssignSParameters('offset',Offset(f,offsetDelay,offsetZ0,offsetLoss))
        sd.AssignSParameters('C',TerminationCPolynomial(f,C0*1e-15,C1*1e-27,C2*1e-36,C3*1e-45))
        sspn=SystemSParametersNumeric(sd)
        SParameters.__init__(self,f,sspn.SParameters().m_d)
