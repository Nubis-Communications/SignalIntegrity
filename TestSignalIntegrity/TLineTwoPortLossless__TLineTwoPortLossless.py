def TLineTwoPortLossless(Zc,Td,f,Z0):
    gamma=1j*2.*math.pi*f*Td
    return TLineTwoPort(Zc,gamma,Z0)