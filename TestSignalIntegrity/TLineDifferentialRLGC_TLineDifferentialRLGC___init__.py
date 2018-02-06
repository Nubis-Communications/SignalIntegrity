class TLineDifferentialRLGC(SParameters):
    def __init__(self,f, Rp, Rsep, Lp, Gp, Cp, dfp,
                         Rn, Rsen, Ln, Gn, Cn, dfn,
                         Cm, dfm, Gm, Lm, Z0, K=0):
        self.m_K=K
        self.balanced = Rp==Rn and Rsep==Rsen and Lp==Ln and Gp==Gn and Cp==Cn
        if K==0 and self.balanced:
            self.Rp=Rp;     self.Rn=Rn
            self.Rsep=Rsep; self.Rsen=Rsen
            self.Lp=Lp;     self.Ln=Ln
            self.Gp=Gp;     self.Gn=Gn
            self.Cp=Cp;     self.Cn=Cn
            self.dfp=dfp;   self.dfn=dfn
            self.Cm=Cm;     self.dfm=dfm
            self.Gm=Gm;     self.Lm=Lm
            sdp=SystemDescriptionParser()
            # Ports 1 2 3 4 are + - D C of mixed mode converter
            sdp.AddLines(['device L 4 mixedmode',
                          'device R 4 mixedmode',
                          'device TE 2','device TO 2',
                          'port 1 L 1','port 2 R 1',
                          'port 3 L 2','port 4 R 2',
                          'connect L 3 TO 1',
                          'connect R 3 TO 2',
                          'connect L 4 TE 1',
                          'connect R 4 TE 2'])
            self.sd=sdp.SystemDescription()
        else:
            self.m_approx=TLineDifferentialRLGCApproximate(f,
                    Rp, Rsep, Lp, Gp, Cp, dfp,
                    Rn, Rsen, Ln, Gn, Cn, dfn,
                    Cm, dfm, Gm, Lm, Z0, K)
        SParameters.__init__(self,f,None,Z0)
    def __getitem__(self,n):
        if self.m_K==0 and self.balanced:
            f=self.m_f[n]
            Ze=self.Rp+self.Rsep*math.sqrt(f)+1j*2*math.pi*f*(self.Lp+self.Lm)
            Ye=self.Gp+2.*math.pi*f*self.Cp*(1j+self.dfp)
            try:
                Zce=cmath.sqrt(Ze/Ye)
            except:
                Zce=self.m_Z0
            gammae=cmath.sqrt(Ze*Ye)
            Te=TLineTwoPort(Zce,gammae,self.m_Z0)
            self.sd.AssignSParameters('TE',Te)
            Zo=self.Rp+self.Rsep*math.sqrt(f)+1j*2*math.pi*f*(self.Lp-self.Lm)
            Yo=self.Gp+2.*self.Gm+2.*math.pi*f*self.Cp*(1j+self.dfp)+\
                2.*math.pi*f*2.*self.Cm*(1j+self.dfm)
            try:
                Zco=cmath.sqrt(Zo/Yo)
            except:
                Zco=self.m_Z0
            gammao=cmath.sqrt(Zo*Yo)
            To=TLineTwoPort(Zco,gammao,self.m_Z0)
            self.sd.AssignSParameters('TO',To)
            return SystemSParametersNumeric(self.sd).SParameters()
        else: return self.m_approx[n]
