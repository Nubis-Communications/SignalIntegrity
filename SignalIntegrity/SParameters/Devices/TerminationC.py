from SignalIntegrity.SParameters.SParameters import SParameters
import SignalIntegrity.Devices as dev

class TerminationC(SParameters):
    def __init__(self,f,C,Z0=50.):
        self.m_C=C
        SParameters.__init__(self,f,None,Z0)
    def __getitem__(self,n):
        return dev.TerminationC(self.m_C,self.m_f[n],self.m_Z0)