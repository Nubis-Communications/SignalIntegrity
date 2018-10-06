def TLineTwoPort(Zc,gamma,Z0):
    p=(Zc-Z0)/(Zc+Z0)
    L=cmath.exp(-gamma)
    S1=(p*(1.-L*L))/(1.-p*p*L*L)
    S2=((1.-p*p)*L)/(1.-p*p*L*L)
    return [[S1,S2],[S2,S1]]