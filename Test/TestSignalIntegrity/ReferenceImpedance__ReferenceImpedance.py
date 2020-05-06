def ReferenceImpedance(S,Z0f,Z0i=None,Kf=None,Ki=None):
    (Z0f,Kf)=Z0KHelper((Z0f,Kf),len(S))
    (Z0i,Ki)=Z0KHelper((Z0i,Ki),len(S))
    I=array(identity(len(S)))
    p=(array(Z0f)-array(Z0i)).dot(inv(array(Z0f)+array(Z0i)))
    Kf=array(Ki).dot(inv(array(Kf)))
    S=array(S)
    return (Kf.dot(inv(I-p)).dot(S-p).dot(
        inv(I-p.dot(S))).dot(I-p).dot(inv(Kf))).tolist()
