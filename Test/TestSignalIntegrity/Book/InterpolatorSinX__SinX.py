def SinX(S,U,F):
    sl=[1. if float(k)/U-F-S==0 else
        math.sin(math.pi*(float(k)/U-F-S))/(math.pi*(float(k)/U-F-S))*\
        (1./2.+1./2.*math.cos(math.pi*(float(k)/U-S)/S))
        for k in range(2*U*S+1)]
    s=sum(sl)/U
    sl=[sle/s for sle in sl]
    return sl

