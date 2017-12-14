'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''

from SignalIntegrity.SystemDescriptions.SystemSParametersNumeric import SystemSParametersNumeric
from SignalIntegrity.Measurement.CalKit.Standards.TerminationPolynomial import TerminationLPolynomial
from SignalIntegrity.Measurement.CalKit.Standards.Offset import Offset
from SignalIntegrity.SParameters.SParameters import SParameters

class ShortStandard(SParameters):
    def __init__(self,f,offsetDelay=0.0,offsetZ0=50.0,offsetLoss=0.0,
                 L0=0.0,L1=0.0,L2=0.0,L3=0.0):
        # pragma: silent exclude
        from SignalIntegrity.Parsers.SystemDescriptionParser import SystemDescriptionParser
        # pragma: include
        sspn=SystemSParametersNumeric(SystemDescriptionParser().AddLines(
            ['device offset 2','device L 1','port 1 offset 1','connect offset 2 L 1']
            ).SystemDescription())
        offsetSParameters=Offset(f,offsetDelay,offsetZ0,offsetLoss)
        terminationSParameters=TerminationLPolynomial(f,L0,L1,L2,L3)
        sp=[]
        for n in range(len(f)):
            sspn.AssignSParameters('offset',offsetSParameters[n])
            sspn.AssignSParameters('L',terminationSParameters[n])
            sp.append(sspn.SParameters())
        SParameters.__init__(self,f,sp)