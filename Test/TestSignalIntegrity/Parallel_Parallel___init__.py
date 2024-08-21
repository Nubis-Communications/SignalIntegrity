class Parallel(SParameters):
    def __init__(self,f:list, name:str, numberInParallel:float, Z0:float =50, **kwargs):
        self.m_K=numberInParallel
        sdp=SystemDescriptionParser().AddLines(['device D 2','port 1 D 1 2 D 2 3 D 1 4 D 2'])
        self.m_dev=SParameterFile(name,None,None,**kwargs).Resample(f).SetReferenceImpedance(Z0)
        self.m_sspn1=SystemSParametersNumeric(sdp.SystemDescription())
        sdp=SystemDescriptionParser().AddLines(['device D 4','device O1 1 open','device O2 1 open',
                                    'connect O1 1 D 3','connect O2 1 D 4','port 1 D 1 2 D 2'])
        self.m_sspn2=SystemSParametersNumeric(sdp.SystemDescription())
        SParameters.__init__(self,f,None,Z0)
    def __getitem__(self,n: int):
        self.m_sspn1.AssignSParameters('D',self.m_dev[n])
        sp=self.m_sspn1.SParameters()
        lp=[1,2]; rp=[3,4]
        sp=T2S(linalg.fractional_matrix_power(S2T(sp,lp,rp),self.m_K),lp,rp)
        self.m_sspn2.AssignSParameters('D', sp)
        sp=self.m_sspn2.SParameters()
        sp=ReferenceImpedance(sp,self.m_Z0,self.m_dev.m_Z0)
        return sp
