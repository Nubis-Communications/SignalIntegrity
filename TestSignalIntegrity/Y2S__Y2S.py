def Y2S(Y,Z0=None,K=None):
    (Z0,K)=Z0KHelper((Z0,K),len(Y))
    I=matrix(identity(len(Y)))
    Y=matrix(Y)
    return (K.getI()*(I+Z0*Y).getI()*(I-Z0*Y)*K).tolist()
