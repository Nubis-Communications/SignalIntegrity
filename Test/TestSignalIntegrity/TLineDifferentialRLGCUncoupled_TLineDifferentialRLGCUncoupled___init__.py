class TLineDifferentialRLGCUncoupled(SParameters):
    def __init__(self,f,Rp,Rsep,Lp,Gp,Cp,dfp,Rn,Rsen,Ln,Gn,Cn,dfn,Z0,K=0):
        sdp=SystemDescriptionParser()
        sdp.AddLines(['device TP 2','device TN 2',
                      'port 1 TP 1 2 TN 1 3 TP 2 4 TN 2'])
        self.m_sspn=SystemSParametersNumeric(sdp.SystemDescription())
        self.m_spdl=[('TP',TLineTwoPortRLGC(f,Rp,Rsep,Lp,Gp,Cp,dfp,Z0,K)),
                     ('TO',TLineTwoPortRLGC(f,Rn,Rsen,Ln,Gn,Cn,dfn,Z0,K))]
        SParameters.__init__(self,f,None,Z0)
    def __getitem__(self,n):
        for ds in self.m_spdl:
            self.m_sspn.AssignSParameters(ds[0],ds[1][n])
        return self.m_sspn.SParameters()