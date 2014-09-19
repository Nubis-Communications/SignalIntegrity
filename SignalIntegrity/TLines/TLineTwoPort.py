import cmath

def TLineSE(Zc,gamma,Z0):
    p=(Zc-Z0)/(Zc+Z0)
    L=cmath.exp(-gamma)
    S1=(p*(1-L^2))/(1-p^2*L^2)
    S2=((1-p^2)*L)/(1-p^2*L^2)
    return [[S1,S2],[S2,S1]]