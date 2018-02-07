'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
from SignalIntegrity.SParameters.SParameters import SParameters

"""
    ports are 1,2,3,4 is +1,-1, +2, -2
"""
class TLineDifferentialRLGCUncoupled(SParameters):
    def __init__(self,f,Rp,Rsep,Lp,Gp,Cp,dfp,Rn,Rsen,Ln,Gn,Cn,dfn,Z0,K=0):
        # pragma: silent exclude
        from SignalIntegrity.Parsers.SystemDescriptionParser import SystemDescriptionParser
        from SignalIntegrity.SystemDescriptions.SystemSParametersNumeric import SystemSParametersNumeric
        from SignalIntegrity.SParameters.Devices.TLineTwoPortRLGC import TLineTwoPortRLGC
        # pragma: include
        sdp=SystemDescriptionParser()
        sdp.AddLines(['device TP 2','device TN 2',
                      'port 1 TP 1 2 TN 1 3 TP 2 4 TN 2'])
        self.m_sspn=SystemSParametersNumeric(sdp.SystemDescription())
        self.m_spdl=[('TP',TLineTwoPortRLGC(f,Rp,Rsep,Lp,Gp,Cp,dfp,Z0,K)),
                     ('TO',TLineTwoPortRLGC(f,Rn,Rsen,Ln,Gn,Cn,dfn,Z0,K))]
        SParameters.__init__(self,f,None,Z0)
    def __getitem__(self,n):
        for ds in self.m_spdl:
            self.m_sspn.AssignSParameters(ds[0],ds[1][n])
        return self.m_sspn.SParameters()