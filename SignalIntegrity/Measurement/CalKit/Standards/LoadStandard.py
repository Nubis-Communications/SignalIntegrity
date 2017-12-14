'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''

from SignalIntegrity.SystemDescriptions.SystemSParametersNumeric import SystemSParametersNumeric
from SignalIntegrity.SParameters.SParameters import SParameters
from SignalIntegrity.Devices.TerminationZ import TerminationZ

from SignalIntegrity.Measurement.CalKit.Standards.Offset import Offset

class LoadStandard(SParameters):
    def __init__(self,f,offsetDelay=0.0,offsetZ0=50.0,offsetLoss=0.0,
                 terminationZ0=50.0):
        # pragma: silent exclude
        from SignalIntegrity.Parsers.SystemDescriptionParser import SystemDescriptionParser
        # pragma: include
        sspn=SystemSParametersNumeric(SystemDescriptionParser().AddLines(
            ['device offset 2','device R 1','port 1 offset 1','connect offset 2 R 1']
            ).SystemDescription())
        offsetSParameters=Offset(f,offsetDelay,offsetZ0,offsetLoss)
        terminationSParameters=TerminationZ(terminationZ0)
        sp=[]
        for n in range(len(f)):
            sspn.AssignSParameters('offset',offsetSParameters[n])
            sspn.AssignSParameters('R',terminationSParameters)
            sp.append(sspn.SParameters())
        SParameters.__init__(self,f,sp)
