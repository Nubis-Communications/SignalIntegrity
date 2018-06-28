def TLineTwoPortLossless(Zc,Td,f,Z0=50.):
    return TLineTwoPort(Zc,1j*2.*math.pi*f*Td,Z0)