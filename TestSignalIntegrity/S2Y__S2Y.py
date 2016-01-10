def S2Y(S,Z0=None,K=None):
    (Z0,K)=Z0KHelper((Z0,K),len(S))
    I=matrix(identity(len(S)))
    S=matrix(S)
    return (K*Z0.getI()*(I-S)*(I+S).getI()*K.getI()).tolist()

