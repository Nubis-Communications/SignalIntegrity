class TLineTwoPortRLGCAnalytic(SParameters):
    def __init__(self,f, R, Rse, L, G, C, df, Z0=50., scale=1.):
        self.R=R*scale;   self.Rse=Rse*scale; self.L=L*scale
        self.G=G*scale;   self.C=C*scale;     self.df=df
        SParameters.__init__(self,f,None,Z0)
    def __getitem__(self,n):
        f=self.m_f[n]
        Z=self.R+self.Rse*(1+1j)*math.sqrt(f)+1j*2*math.pi*f*self.L
        Y=self.G+2.*math.pi*f*self.C*(1j+self.df)
        try: Zc=cmath.sqrt(Z/Y)
        except: return SeriesZ(Z)
        gamma=cmath.sqrt(Z*Y)
        return TLineTwoPort(Zc,gamma,self.m_Z0)
