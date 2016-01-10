def Sp2Sw(Sp,Z0w=None,Z0p=None,Kw=None,Kp=None):
    if Z0p is None:
        Z0p=Z0w
    (Z0w,Kw)=Z0KHelper((Z0w,Kw),len(Sp))
    (Z0p,Kp)=Z0KHelperPW((Z0p,Kp),len(Sp))
    Sp=matrix(Sp)
    Sw=(Kw.getI()*Kp*Z0p.real.getI()*((Z0p.conjugate()-Z0w)+(Z0p+Z0w)*Sp)*
        ((Z0p.conjugate()+Z0w)+(Z0p-Z0w)*Sp).getI()*Kw*Kp.getI()*Z0p.real)
    return Sw