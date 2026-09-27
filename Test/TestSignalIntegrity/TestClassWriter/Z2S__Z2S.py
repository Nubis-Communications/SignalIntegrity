def Z2S(Z,Z0=None,K=None):
    (Z0,K)=Z0KHelper((Z0,K),len(Z))
    Z=array(Z)
    return (inv(K).dot(Z-Z0).dot(inv(Z+Z0)).dot(K)).tolist()
