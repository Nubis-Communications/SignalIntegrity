def Sw2Sp(Sp,Z0w=None,Z0p=None,Kw=None):
    if Z0p is None:
        Z0p=Z0w
    (Z0w,Kw)=Z0KHelper((Z0w,Kw),len(Sp))
    (Z0p,Kp)=Z0KHelperPW(Z0p,len(Sp))
    Sp=array(Sp)
    Sw=inv(Kp).dot(Kw).dot(inv(Z0w)).dot((Z0w-Z0p.conj())+(Z0w+Z0p.conj()).dot(
        Sp)).dot(inv((Z0w+Z0p)+(Z0w-Z0p).dot(Sp)).dot(Kp).dot(inv(Kw)).dot(Z0w))
    return Sw.tolist()
