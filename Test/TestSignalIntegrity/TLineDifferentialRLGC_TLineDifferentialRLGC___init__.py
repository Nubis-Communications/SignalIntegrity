class TLineDifferentialRLGC(SParameters):
    def __init__(self,f, Rp, Rsep, Lp, Gp, Cp, dfp,
                         Rn, Rsen, Ln, Gn, Cn, dfn,
                         Cm, dfm, Gm, Lm, Z0, K=0):
        balanced = Rp==Rn and Rsep==Rsen and Lp==Ln and Gp==Gn and Cp==Cn
        uncoupled = Cm==0 and (Cm != 0 and dfm==0) and Gm==0 and Lm==0
        if K != 0 or (not balanced and not uncoupled):
            if K==0:
                # max possible electrical length
                Td=math.sqrt((max(Lp,Ln)+Lm)*(max(Cp,Cn)+2*Cm))
                Rt=0.45/f[-1] # fastest risetime
                # sections such that fraction of risetime less than round trip
                # electrical length of one section
                K=int(math.ceil(Td*2/(Rt*self.rtFraction)))
            self.sp=TLineDifferentialRLGCApproximate(f,
                        Rp, Rsep, Lp, Gp, Cp, dfp,
                        Rn, Rsen, Ln, Gn, Cn, dfn,
                        Cm, dfm, Gm, Lm, Z0, K)
        elif uncoupled:
            self.sp=TLineDifferentialRLGCUncoupled(f,
                        Rp, Rsep, Lp, Gp, Cp, dfp,
                        Rn, Rsen, Ln, Gn, Cn, dfn,
                        Z0, K)
        elif balanced:
            self.sp=TLineDifferentialRLGCBalanced(f,
                        Rp, Rsep, Lp, Gp, Cp, dfp,
                        Cm, dfm, Gm, Lm, Z0, K)
        SParameters.__init__(self,f,None,Z0)
    def __getitem__(self,n):
        return self.sp[n]