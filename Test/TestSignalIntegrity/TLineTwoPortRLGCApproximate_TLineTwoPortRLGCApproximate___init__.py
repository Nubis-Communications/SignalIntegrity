class TLineTwoPortRLGCApproximate(SParameters):
    def __init__(self,f, R, Rse, L, G, C, df, Z0=50., K=0, scale=1.):
        R=R*scale; Rse=Rse*scale; L=L*scale; G=G*scale; C=C*scale; df=df
        K=int(K*scale+0.5)
        if K==0:
            Td=math.sqrt(L*C)
            Rt=0.45/f[-1] # fastest risetime
            K=int(math.ceil(Td*2/(Rt*self.rtFraction)))

        self.m_K=K
        sdp=SystemDescriptionParser().AddLines(['device R 2','device Rse 2',
        'device L 2','device C 1','device G 1','connect R 2 Rse 1',
        'connect Rse 2 L 1','connect L 2 G 1 C 1','port 1 R 1 2 G 1'])
        self.m_sspn=SystemSParametersNumeric(sdp.SystemDescription())
        self.m_sspn.AssignSParameters('R',SeriesZ(R/K,Z0))
        self.m_sspn.AssignSParameters('G',TerminationG(G/K,Z0))
        self.m_spdl=[('Rse',SeriesRse(f,Rse/K,Z0)),
                     ('L',SeriesL(f,L/K,Z0)),
                     ('C',TerminationC(f,C/K,Z0,df))]
        SParameters.__init__(self,f,None,Z0)
    def __getitem__(self,n):
        for ds in self.m_spdl: self.m_sspn.AssignSParameters(ds[0],ds[1][n])
        sp=self.m_sspn.SParameters()
        return T2S(linalg.matrix_power(S2T(sp),self.m_K))
