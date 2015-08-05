from numpy import linalg
import math

from SignalIntegrity.Conversions import S2T
from SignalIntegrity.Conversions import T2S
from SignalIntegrity.SParameters.SParameters import SParameters

class ApproximateFourPortTLineOld(SParameters):
    def __init__(self,f, Rsp, Lsp, Csp, Gsp, Rsm, Lsm, Csm, Gsm, Lm, Cm, Gm, Z0, K):
        from SignalIntegrity.Devices import SeriesZ
        from SignalIntegrity.Devices import SeriesG
        from SignalIntegrity.Devices import SeriesC
        from SignalIntegrity.Devices import SeriesL
        from SignalIntegrity.Devices import Ground
        from SignalIntegrity.Devices import Mutual
        import SignalIntegrity.SParameters.Devices as dev
        from SignalIntegrity.SystemDescriptions.SystemSParametersNumeric import SystemSParametersNumeric
        sspn=SystemSParametersNumeric()
        spdl=[]
        sspn.AddDevice('RP',2,SeriesZ(Rsp/K,Z0))
        sspn.AddDevice('RN',2,SeriesZ(Rsm/K,Z0))
        sspn.AddDevice('LP',2), spdl.append(('LP',dev.SeriesL(f,Lsp/K,Z0)))
        sspn.AddDevice('LN',2), spdl.append(('LN',dev.SeriesL(f,Lsm/K,Z0)))
        sspn.AddDevice('M',4), spdl.append(('M',dev.Mutual(f,Lm/K,Z0)))
        sspn.AddDevice('GM',2,SeriesG(Gm/K,Z0))
        sspn.AddDevice('CM',2), spdl.append(('CM',dev.SeriesC(f,Cm/K,Z0)))
        sspn.AddDevice('CP',2), spdl.append(('CP',dev.SeriesC(f,Csp/K,Z0)))
        sspn.AddDevice('CN',2), spdl.append(('CN',dev.SeriesC(f,Csm/K,Z0)))
        sspn.AddDevice('GDP',1,Ground())
        sspn.AddDevice('GDN',1,Ground())
        sspn.AddDevice('GP',2,SeriesG(Gsp/K,Z0))
        sspn.AddDevice('GN',2,SeriesG(Gsm/K,Z0))
        sspn.AddPort('RP',1,1)
        sspn.AddPort('RN',1,2)
        sspn.ConnectDevicePort('RP',2,'LP',1)
        sspn.ConnectDevicePort('RN',2,'LN',1)
        sspn.ConnectDevicePort('LP',2,'M',1)
        sspn.ConnectDevicePort('LN',2,'M',3)
        sspn.ConnectDevicePort('M',2,'GM',1)
        sspn.ConnectDevicePort('M',4,'GM',2)
        sspn.ConnectDevicePort('GM',1,'CM',1)
        sspn.ConnectDevicePort('GM',2,'CM',2)
        sspn.ConnectDevicePort('CM',1,'CP',1)
        sspn.ConnectDevicePort('CM',2,'CN',1)
        sspn.ConnectDevicePort('CP',2,'GDP',1)
        sspn.ConnectDevicePort('CN',2,'GDN',1)
        sspn.ConnectDevicePort('GP',1,'CP',1)
        sspn.ConnectDevicePort('GP',2,'CP',2)
        sspn.ConnectDevicePort('GN',1,'CN',1)
        sspn.ConnectDevicePort('GN',2,'CN',2)
        sspn.AddPort('GM',1,3)
        sspn.AddPort('GM',2,4)
        sp=[]
        for n in range(len(f)):
            for ds in spdl: sspn.AssignSParameters(ds[0],ds[1][n])
            sp.append(T2S(linalg.matrix_power(S2T(sspn.SParameters()),K)))
        SParameters.__init__(self,f,sp)

class ApproximateFourPortTLine(SParameters):
    def __init__(self,f, Rsp, Lsp, Csp, Gsp, Rsm, Lsm, Csm, Gsm, Lm, Cm, Gm, Z0, K):
        self.m_K=K
        from SignalIntegrity.Devices import SeriesG
        from SignalIntegrity.Devices import SeriesC
        from SignalIntegrity.Devices import Mutual
        import SignalIntegrity.SParameters.Devices as dev
        from SignalIntegrity.SystemDescriptions.SystemSParametersNumeric import SystemSParametersNumeric
        self.m_sspn=SystemSParametersNumeric()
        self.m_spdl=[]
        self.m_sspn.AddDevice('TP',2), self.m_spdl.append(('TP',dev.ApproximateTwoPortTLine(f,Rsp/K,Lsp/K,Gsp/K,Csp/K,Z0,1)))
        self.m_sspn.AddDevice('TN',2), self.m_spdl.append(('TN',dev.ApproximateTwoPortTLine(f,Rsm/K,Lsm/K,Gsm/K,Csm/K,Z0,1)))
        self.m_sspn.AddDevice('M',4), self.m_spdl.append(('M',dev.Mutual(f,Lm/K,Z0)))
        self.m_sspn.AddDevice('GM',2,SeriesG(Gm/K,Z0))
        self.m_sspn.AddDevice('CM',2), self.m_spdl.append(('CM',dev.SeriesC(f,Cm/K,Z0)))
        self.m_sspn.AddPort('M',1,1)
        self.m_sspn.AddPort('M',3,2)
        self.m_sspn.ConnectDevicePort('M',2,'TP',1)
        self.m_sspn.ConnectDevicePort('M',4,'TN',1)
        self.m_sspn.ConnectDevicePort('TP',2,'GM',1)
        self.m_sspn.ConnectDevicePort('TN',2,'GM',2)
        self.m_sspn.ConnectDevicePort('TP',2,'CM',1)
        self.m_sspn.ConnectDevicePort('TN',2,'CM',2)
        self.m_sspn.AddPort('TP',2,3)
        self.m_sspn.AddPort('TN',2,4)
        SParameters.__init__(self,f,None,Z0)
    def __getitem__(self,n):
        for ds in self.m_spdl: self.m_sspn.AssignSParameters(ds[0],ds[1][n])
        return T2S(linalg.matrix_power(S2T(self.m_sspn.SParameters()),self.m_K))
