def ReferenceImpedance(S,Z0f,Z0i=None,Kf=None,Ki=None):
    (Z0f,Kf)=Z0KHelper((Z0f,Kf),len(S))
    (Z0i,Ki)=Z0KHelper((Z0i,Ki),len(S))
    I=matrix(identity(len(S)))
    p=(matrix(Z0f)-matrix(Z0i))*(matrix(Z0f)+matrix(Z0i)).getI()
    Kf=matrix(Ki)*matrix(Kf).getI()
    S=matrix(S)
    return (Kf*(I-p).getI()*(S-p)*(I-p*S).getI()*(I-p)*Kf.getI()).tolist()

