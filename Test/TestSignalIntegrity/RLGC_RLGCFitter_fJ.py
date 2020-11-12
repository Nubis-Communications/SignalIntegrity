class RLGCFitter(LevMar):
    def fJ(self,a,Fa=None):
        if self.m_Fa is None: self.m_Fa=self.fF(a)
        (R,L,G,C,Rse,df)=(a[0][0],a[1][0],a[2][0],a[3][0],a[4][0],a[5][0])
        dZ=[self.dZdR,self.dZdL,self.dZdG,self.dZdC,self.dZdRse,self.dZddf]
        dYdC=[p2f*(1j+df) for p2f in self.p2f]
        dYddf=[p2f*C for p2f in self.p2f]
        dY=[self.dYdR,self.dYdL,self.dYdG,dYdC,self.dYdRse,dYddf]
        dgamma=[[1./(2.*cmath.sqrt(z*y))*(dz*y+z*dy)
                for (z,y,dz,dy) in zip(self.Z,self.Y,dZ[i],dY[i])]
                    for i in range(6)]
        dZc=[[-1./2*(-dz*y+z*dy)/(y*y*cmath.sqrt(z/y))
                for (z,y,dz,dy) in zip(self.Z,self.Y,dZ[i],dY[i])]
                    for i in range(6)]
        drho=[[2.*dzc*self.Z0/((zc+self.Z0)*(zc+self.Z0))
                for (zc,dzc) in zip(self.Zc,dZc[i])] for i in range(6)]
        D2=[d*d for d in self.D]
        dS11=[[-2.*r*e2*(r2-1)/d2*dg+(1-e2)*(1+r2*e2)/d2*dr
                for (r,r2,e2,d2,dg,dr) in
                    zip(self.rho,self.rho2,self.e2g,D2,dgdx,drdx)]
                            for (dgdx,drdx) in zip(dgamma,drho)]
        dS12=[[e*(r2-1)*(1+r2*e2)/d2*dg-2.*r*e*(1-e2)/d2*dr
                for (r,r2,e,e2,d2,dg,dr) in
                    zip(self.rho,self.rho2,self.eg,self.e2g,D2,dgdx,drdx)]
                            for (dgdx,drdx) in zip(dgamma,drho)]
        dS=[[[[dS11[i][n],dS12[i][n]],[dS12[i][n],dS11[i][n]]]
                for n in range(len(self.f))] for i in range(6)]
        vdS=[self.VectorizeSp(ds) for ds in dS]
        return array([[vdS[m][r][0] for m in range(len(a))] for r in range(len(Fa))])
...
