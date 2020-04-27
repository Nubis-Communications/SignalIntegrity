def Y2S(Y,Z0=None,K=None):
    (Z0,K)=Z0KHelper((Z0,K),len(Y))
    I=array(identity(len(Y)))
    Y=array(Y)
    return (inv(K).dot(inv(I+Z0.dot(Y))).dot(I-Z0.dot(Y)).dot(K)).tolist()
