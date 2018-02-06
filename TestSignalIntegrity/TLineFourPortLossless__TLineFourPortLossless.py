def TLineFourPortLossless(Zc,Td,f,Z0):
    return TLineFourPort(Zc,1j*2.*math.pi*f*Td,Z0)