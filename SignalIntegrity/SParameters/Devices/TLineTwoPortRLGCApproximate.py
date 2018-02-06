'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
from SignalIntegrity.SParameters.SParameters import SParameters

class TLineTwoPortRLGCApproximate(SParameters):
    def __init__(self,f, R, Rse, L, G, C, df, Z0, K):
        self.m_K=K
        # pragma: silent exclude
        from SignalIntegrity.Devices import SeriesZ
        from SignalIntegrity.Devices import TerminationG
        from SignalIntegrity.SParameters.Devices.TerminationC import TerminationC
        from SignalIntegrity.SParameters.Devices.SeriesL import SeriesL
        from SignalIntegrity.SParameters.Devices.SeriesRse import SeriesRse
        from SignalIntegrity.SystemDescriptions.SystemSParametersNumeric import SystemSParametersNumeric
        from SignalIntegrity.Parsers.SystemDescriptionParser import SystemDescriptionParser
        # pragma: include
        sdp=SystemDescriptionParser().AddLines(['device R 2','device Rse 2',
        'device L 2','device C 1','device G 1','connect R 2 Rse 1',
        'connect Rse 2 L 1','connect L 2 G 1 C 1','port 1 R 1 2 G 1'])
        self.m_sspn=SystemSParametersNumeric(sdp.SystemDescription())
        self.m_sspn.AssignSParameters('R',SeriesZ(R/K,Z0))
        self.m_sspn.AssignSParameters('G',TerminationG(G/K,Z0))
        self.m_spdl=[('Rse',SeriesRse(f,Rse/K,Z0)),
                     ('L',SeriesL(f,L/K,Z0)),
                     ('C',TerminationC(f,C/K,Z0,df))]
        SParameters.__init__(self,f,None,Z0)
    def __getitem__(self,n):
        # pragma: silent exclude
        from numpy import linalg
        from SignalIntegrity.Conversions import S2T
        from SignalIntegrity.Conversions import T2S
        # pragma: include
        for ds in self.m_spdl:
            self.m_sspn.AssignSParameters(ds[0],ds[1][n])
        sp=self.m_sspn.SParameters()
        if sp == 1: return sp
        return T2S(linalg.matrix_power(S2T(sp),self.m_K))
