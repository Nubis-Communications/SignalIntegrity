class TLineLossless(SParameters):
    def __init__(self,f,P,Zc,Td,Z0=50.):
        self.m_Zc=Zc
        self.m_Td=Td
        self.m_P=P
        SParameters.__init__(self,f,None,Z0)
    def __getitem__(self,n):
        if self.m_P==2:
            return dev.TLineTwoPortLossless(
                self.m_Zc,self.m_Td,self.m_f[n],self.m_Z0)
        elif self.m_P==4:
            return dev.TLineFourPortLossless(
                self.m_Zc,self.m_Td,self.m_f[n],self.m_Z0)
