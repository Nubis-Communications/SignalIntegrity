def S2Z(S,Z0=None,K=None):
    (Z0,K)=Z0KHelper((Z0,K),len(S))
    I=identity(len(S))
    S=array(S)
    result = (K.dot(I+S).dot(inv(I-S)).dot(Z0).dot(inv(K))).tolist()
    return result