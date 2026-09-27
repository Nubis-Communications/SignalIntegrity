def Sp2Sw(Sp,Z0w=None,Z0p=None,Kw=None):
    if Z0p is None:
        Z0p=Z0w
    (Z0w,Kw)=Z0KHelper((Z0w,Kw),len(Sp))
    (Z0p,Kp)=Z0KHelperPW(Z0p,len(Sp))
    Sp=array(Sp)
    Sw=inv(Kw).dot(Kp).dot(inv(Z0p.real)).dot((Z0p.conj()-Z0w)+(Z0p+Z0w).dot(Sp)).dot(
        inv((Z0p.conj()+Z0w)+(Z0p-Z0w).dot(Sp))).dot(Kw).dot(inv(Kp)).dot(Z0p.real)
    return Sw.tolist()
