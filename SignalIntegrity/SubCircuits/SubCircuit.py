'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
from SignalIntegrity.SParameters import SParameters

class SubCircuit(SParameters):
    def __init__(self,f,fileName,args):
        from SignalIntegrity.Parsers import SystemSParametersNumericParser
        sspnp=SystemSParametersNumericParser(f,args).File(fileName)
        SParameters.__init__(self,f,sspnp.SParameters())