class TLineTwoPortRLGCAnalytic(SParameters):
    def __init__(self,f, R, Rse, L, G, C, df, Z0):
        self.R=R
        self.Rse=Rse
        self.L=L
        self.G=G
        self.C=C
        self.df=df
        SParameters.__init__(self,f,None,Z0)
    def __getitem__(self,n):
        f=self.m_f[n]
        Z=self.R+self.Rse*math.sqrt(f)+1j*2*math.pi*f*self.L
        Y=self.G+2.*math.pi*f*self.C*(1j+self.df)
        try:
            Zc=cmath.sqrt(Z/Y)
        except:
            Zc=self.m_Z0
        gamma=cmath.sqrt(Z*Y)
        return TLineTwoPort(Zc,gamma,self.m_Z0)
