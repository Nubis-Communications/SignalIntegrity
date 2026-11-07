class RLGCFitter(LevMar):
    def fJ(self,a,Fa=None):
        if self.m_Fa is None: self.m_Fa=self.fF(a)
        (R,L,G,C,Rse,df)=(a[0][0],a[1][0],a[2][0],a[3][0],a[4][0],a[5][0])
        Z=self.Z; Y=self.Y; gamma=self.gamma; Zc=self.Zc
        rho=self.rho; rho2=self.rho2; eg=self.eg; e2g=self.e2g
        dZ=[self.onesarr,1j*self.p2farr,self.zerosarr,
            self.zerosarr,self.dZdRsearr,self.zerosarr]
        dY=[self.zerosarr,self.zerosarr,self.onesarr,
            self.p2farr*(1j+df),self.zerosarr,self.p2farr*C]
        D2=self.D*self.D
        J=np.empty((4*len(self.f),len(a)),dtype=complex)
        for m in range(len(a)):
            dgamma=(dZ[m]*Y+Z*dY[m])/(2.*gamma)
            dZc=-1./2*(-dZ[m]*Y+Z*dY[m])/(Y*Y*Zc)
            drho=2.*dZc*self.Z0/((Zc+self.Z0)*(Zc+self.Z0))
            dS11=-2.*rho*e2g*(rho2-1)/D2*dgamma+(1-e2g)*(1+rho2*e2g)/D2*drho
            dS12=eg*(rho2-1)*(1+rho2*e2g)/D2*dgamma-2.*rho*eg*(1-e2g)/D2*drho
            J[0::4,m]=dS11; J[1::4,m]=dS12; J[2::4,m]=dS12; J[3::4,m]=dS11
        return J
...
