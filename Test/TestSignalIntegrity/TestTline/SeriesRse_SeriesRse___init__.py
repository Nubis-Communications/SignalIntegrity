class SeriesRse(SParameters):
    def __init__(self,f,Rse,Z0=50.):
        self.m_Rse=Rse
        SParameters.__init__(self,f,None,Z0)
    def __getitem__(self,n):
        return dev.SeriesRse(self.m_f[n],self.m_Rse,self.m_Z0)
