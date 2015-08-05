from SignalIntegrity.SParameters.SParameters import SParameters
import SignalIntegrity.Devices as dev
from numpy import math

# primary is ports 1 and 2, secondary is ports 3 and 4
# dot on ports 1 and 3
class Mutual(SParameters):
    def __init__(self,f,M,Z0=50.):
        self.m_M=M
        SParameters.__init__(self,f,None,Z0)
    def __getitem__(self,n):
        return dev.Mutual(0.,0.,self.m_M,1j*2.*math.pi*self.m_f[n],self.m_Z0)