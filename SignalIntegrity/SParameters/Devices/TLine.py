from SignalIntegrity.SParameters.SParameters import SParameters
import SignalIntegrity.Devices as dev
from numpy import math

class TLine(SParameters):
    def __init__(self,f,P,Zc,Gamma,Z0=50.):
        SParameters.__init__(self,f,None,Z0)
        self.m_Zc=Zc
        self.m_Gamma=Gamma
        self.m_P=P
    def __getitem__(self,n):
        if self.m_P==2:
            return dev.TLineSE(self.m_Zc,1j*2.*math.pi*self.m_f[n]*self.m_Gamma,self.m_Z0)
        elif self.m_P==4:
            return dev.TLineFourPort(self.m_Zc,self.m_Gamma,self.m_f[n],self.m_Z0)
