def S2Y(S,Z0=None,K=None):
    (Z0,K)=Z0KHelper((Z0,K),len(S))
    I=identity(len(S))
    S=array(S)
    return (K.dot(inv(Z0)).dot(I-S).dot(inv(I+S)).dot(inv(K))).tolist()
