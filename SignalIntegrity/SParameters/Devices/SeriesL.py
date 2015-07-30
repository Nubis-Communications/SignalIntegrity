from SignalIntegrity.SParameters.SParameters import SParameters
import SignalIntegrity.Devices as dev

class SeriesL(SParameters):
    def __init__(self,f,L,Z0=50.):
        SParameters.__init__(self,f,None,Z0)
        self.m_L=L
    def __getitem__(self,n):
        return dev.SeriesL(self.m_L,self.m_f[n],self.m_Z0)