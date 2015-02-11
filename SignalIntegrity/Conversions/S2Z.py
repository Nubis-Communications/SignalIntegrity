from numpy import matrix
from numpy import identity

from Z0KHelper import Z0KHelper

def S2Z(S,Z0=None,K=None):
    (Z0,K)=Z0KHelper((Z0,K),len(S))
    I=matrix(identity(len(S)))
    S=matrix(S)
    return (K*(I+S)*(I-S).getI()*Z0*K.getI()).tolist()