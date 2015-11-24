from numpy import linalg
import math

from SignalIntegrity.Conversions import S2T
from SignalIntegrity.Conversions import T2S
from SignalIntegrity.SParameters.SParameters import SParameters

class ApproximateTwoPortTLine(SParameters):
    def __init__(self,f, R, L, G, C, Z0, K):
        self.m_K=K
        from SignalIntegrity.Devices import SeriesZ
        from SignalIntegrity.Devices import SeriesG
        from SignalIntegrity.Devices import SeriesC
        from SignalIntegrity.Devices import SeriesL
        from SignalIntegrity.Devices import Ground
        from SignalIntegrity.Devices import Mutual
        import SignalIntegrity.SParameters.Devices as dev
        from SignalIntegrity.SystemDescriptions.SystemSParametersNumeric import SystemSParametersNumeric
        self.m_sspn=SystemSParametersNumeric()
        self.m_spdl=[]
        self.m_sspn.AddDevice('R',2,SeriesZ(R/K,Z0))
        self.m_sspn.AddDevice('L',2), self.m_spdl.append(('L',dev.SeriesL(f,L/K,Z0)))
        self.m_sspn.AddDevice('C',2), self.m_spdl.append(('C',dev.SeriesC(f,C/K,Z0)))
        self.m_sspn.AddDevice('GD',1,Ground())
        self.m_sspn.AddDevice('G',2,SeriesG(G/K,Z0))
        self.m_sspn.AddPort('R',1,1)
        self.m_sspn.ConnectDevicePort('R',2,'L',1)
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
