from SignalIntegrity.SParameters.SParameters import SParameters
import SignalIntegrity.Devices as dev
from numpy import math

class Mutual(SParameters):
    def __init__(self,f,M,Z0=50.):
        SParameters.__init__(self,f,None,Z0)
        self.m_M=M
    def __getitem__(self,n):
        return dev.Mutual(0.,0.,self.m_M,1j*2.*math.pi*self.m_f[n],self.m_Z0)