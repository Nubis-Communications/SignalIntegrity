def Z2S(Z,Z0=None,K=None):
    (Z0,K)=Z0KHelper((Z0,K),len(Z))
    Z=matrix(Z)
    return (K.getI()*(Z-Z0)*(Z+Z0).getI()*K).tolist()

