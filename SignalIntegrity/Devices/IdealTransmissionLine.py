import cmath

def IdealTransmissionLine(rho,gamma):
    L = cmath.exp(-gamma)
    S11=rho*(1.-L*L)/(1.-rho*rho*L*L)
    S21=(1.-rho*rho)*L/(1.-rho*rho*L*L)
    return [[S11,S21],[S21,S11]]