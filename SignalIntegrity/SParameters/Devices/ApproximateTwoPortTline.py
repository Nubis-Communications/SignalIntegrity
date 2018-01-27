'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
from numpy import linalg

from SignalIntegrity.Conversions import S2T
from SignalIntegrity.Conversions import T2S
from SignalIntegrity.SParameters.SParameters import SParameters

class ApproximateTwoPortTLine(SParameters):
    def __init__(self,f, R, Rse, L, G, C, df, Z0, K):
        self.m_K=K
        from SignalIntegrity.Devices import SeriesZ
        from SignalIntegrity.Devices import SeriesG
        from SignalIntegrity.Devices import Ground
        import SignalIntegrity.SParameters.Devices as dev
        from SignalIntegrity.SystemDescriptions.SystemSParametersNumeric import SystemSParametersNumeric
        self.m_sspn=SystemSParametersNumeric()
        self.m_spdl=[]
        self.m_sspn.AddDevice('R',2,SeriesZ(R/K,Z0))
        self.m_sspn.AddDevice('Rse',2), self.m_spdl.append(('Rse',dev.SeriesRse(f,Rse/K,Z0)))
        self.m_sspn.AddDevice('L',2), self.m_spdl.append(('L',dev.SeriesL(f,L/K,Z0)))
        self.m_sspn.AddDevice('C',2), self.m_spdl.append(('C',dev.SeriesC(f,C/K,Z0,df)))
        self.m_sspn.AddDevice('GD',1,Ground())
        self.m_sspn.AddDevice('G',2,SeriesG(G/K,Z0))
        self.m_sspn.AddPort('R',1,1)
        self.m_sspn.ConnectDevicePort('R',2,'Rse',1)
        self.m_sspn.ConnectDevicePort('Rse',2,'L',1)
        self.m_sspn.ConnectDevicePort('L',2,'G',1)
        self.m_sspn.ConnectDevicePort('G',1,'C',1)
        self.m_sspn.ConnectDevicePort('C',2,'GD',1)
        self.m_sspn.ConnectDevicePort('G',2,'GD',1)
        self.m_sspn.AddPort('G',1,2)
        SParameters.__init__(self,f,None,Z0)
    def __getitem__(self,n):
        for ds in self.m_spdl: self.m_sspn.AssignSParameters(ds[0],ds[1][n])
        sp=self.m_sspn.SParameters()
        if sp == 1: return sp
        return T2S(linalg.matrix_power(S2T(sp),self.m_K))
