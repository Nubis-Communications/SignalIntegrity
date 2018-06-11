def TlineFit(sp):
    stepResponse=sp.FrequencyResponse(2,1).ImpulseResponse().Integral()
    threshold=(stepResponse[len(stepResponse)-1]+stepResponse[0])/2.0
    for k in range(len(stepResponse)):
        if stepResponse[k]>threshold: break
    dly=stepResponse.Times()[k]
    rho=sp.FrequencyResponse(1,1).ImpulseResponse().Integral(scale=False).Measure(dly)
    Z0=sp.m_Z0*(1.+rho)/(1.-rho)
    L=dly*Z0; C=dly/Z0; guess=[0.,L,0.,C,0.,0.]
    (R,L,G,C,Rse,df)=[r[0] for r in si.fit.RLGCFitter(sp,guess).Solve().Results()]
    return si.sp.dev.TLineTwoPortRLGC(sp.f(),R,Rse,L,G,C,df,sp.m_Z0)
