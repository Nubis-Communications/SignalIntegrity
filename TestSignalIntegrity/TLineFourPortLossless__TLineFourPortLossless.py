def TLineFourPortLossless(Zc,Td,f,Z0):
    gamma=1j*2.*math.pi*f*Td
    return TLineFourPort(Zc,gamma,Z0)