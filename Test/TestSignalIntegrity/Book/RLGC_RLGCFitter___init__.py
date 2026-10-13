class RLGCFitter(LevMar):
    def __init__(self,sp,guess,callback=None):
        self.m_sp=sp
        self.f=self.m_sp.m_f
        self.Z0=self.m_sp.m_Z0
        v=self.VectorizeSp(sp)
        LevMar.__init__(self,callback)
        # frequency-dependent base vectors (numpy arrays) used to evaluate the
        # transmission-line s-parameters and their partial derivatives for every
        # frequency at once.  These must be set up before Initialize, which
        # evaluates fF.
        self.farr=np.array(self.f,dtype=float)
        self.sqrtfarr=np.sqrt(self.farr)
        self.p2farr=2.*math.pi*self.farr
        self.onesarr=np.ones(len(self.f))
        self.zerosarr=np.zeros(len(self.f))
        self.dZdRsearr=self.sqrtfarr
        LevMar.Initialize(self, array([[g] for g in guess]), array(v))
    def fF(self,a):
        (R,L,G,C,Rse,df)=(a[0][0],a[1][0],a[2][0],a[3][0],a[4][0],a[5][0])
        if G==0: G=self.epsilonG
        if R==0: R=self.epsilonG
        self.Z=R+Rse*(1+1j)*self.sqrtfarr+1j*self.p2farr*L
        self.Y=G+self.p2farr*C*(1j+df)
        self.gamma=np.sqrt(self.Z*self.Y)
        self.Zc=np.sqrt(self.Z/self.Y)
        self.rho=(self.Zc-self.Z0)/(self.Zc+self.Z0)
        self.rho2=self.rho*self.rho
        self.eg=np.exp(-self.gamma)
        self.e2g=self.eg*self.eg
        self.D=1-self.rho2*self.e2g
        self.S11=self.rho*(1-self.e2g)/self.D
        self.S12=(1-self.rho2)*self.eg/self.D
        # vectorized s-parameters: per frequency the 2x2 matrix [[S11,S12],[S12,S11]]
        # unrolled as [S11,S12,S12,S11]
        vS=np.empty((4*len(self.f),1),dtype=complex)
        vS[0::4,0]=self.S11; vS[1::4,0]=self.S12
        vS[2::4,0]=self.S12; vS[3::4,0]=self.S11
        return vS
...
