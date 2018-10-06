class TLineDifferentialRLGCBalanced(SParameters):
    def __init__(self,f,R,Rse,L,G,C,df,Cm,dfm,Gm,Lm,Z0,K=0):
        sdp=SystemDescriptionParser()
        sdp.AddLines(['device L 4 mixedmode','device R 4 mixedmode','device TE 2',
                      'device TO 2','port 1 L 1 2 L 2 3 R 1 4 R 2','connect L 3 TO 1',
                      'connect R 3 TO 2','connect L 4 TE 1','connect R 4 TE 2'])
        self.m_sspn=SystemSParametersNumeric(sdp.SystemDescription())
        self.m_spdl=[('TE',TLineTwoPortRLGC(f,R,Rse,L+Lm,G,C,df,Z0,K)),
                     ('TO',TLineTwoPortRLGC(f,R,Rse,L-Lm,G+2*Gm,C+2*Cm,
                                        (C*df+2*Cm*dfm)/(C+2*Cm),Z0,K))]
        SParameters.__init__(self,f,None,Z0)
    def __getitem__(self,n):
        for ds in self.m_spdl: self.m_sspn.AssignSParameters(ds[0],ds[1][n])
        return self.m_sspn.SParameters()