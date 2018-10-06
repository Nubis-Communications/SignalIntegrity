def Mutual(Ll,Lr,M,f,Z0=None,K=None):
    s=1j*2.*math.pi*f
    D=s*s*(Ll*Lr-M*M)+2*Z0*s*(Ll+Lr)+4*Z0*Z0
    S11=(s*s*(Ll*Lr-M*M)+2*s*Ll*Z0)/D
    S12=(2*Z0*(s*Lr+2*Z0))/D
    S13=(2*s*M*Z0)/D
    S14=-S13
    S21=S12
    S22=S11
    S23=S14
    S24=S13
    S31=S13
    S32=S23
    S33=(s*s*(Ll*Lr-M*M)+2*s*Lr*Z0)/D
    S34=2*Z0*(s*Ll+2*Z0)/D
    S41=S14
    S42=S24
    S43=S34
    S44=S33
    return [[S11,S12,S13,S14],
            [S21,S22,S23,S24],
            [S31,S32,S33,S34],
            [S41,S42,S43,S44]]