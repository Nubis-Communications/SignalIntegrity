def ReferenceImpedanceTransformer(Z0f,Z0i=None,Kf=None,Ki=None):
    Z0f=float(Z0f.real)+float(Z0f.imag)*1j
    if Z0i is None:
        Z0i=50.0
    Z0i=float(Z0i.real)+float(Z0i.imag)*1j
    if Kf is None:
        Kf=cmath.sqrt(Z0f)
    if Ki is None:
        Ki=cmath.sqrt(Z0i)
    Kf=float(Kf.real)+float(Kf.imag)*1j
    Ki=float(Ki.real)+float(Ki.imag)*1j
    p=(Z0f-Z0i)/(Z0f+Z0i)
    return [[p,(1.0-p)*Kf/Ki],[(1.0+p)*Ki/Kf,-p]]
