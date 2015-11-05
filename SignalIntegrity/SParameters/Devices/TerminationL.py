from SignalIntegrity.SParameters.SParameters import SParameters
import SignalIntegrity.Devices as dev

class TerminationL(SParameters):
    def __init__(self,f,L,Z0=50.):
        self.m_L=L
        SParameters.__init__(self,f,None,Z0)
    def __getitem__(self,n):
        return dev.TerminationL(self.m_L,self.m_f[n],self.m_Z0)