def TransresistanceAmplifier(P,G,Zi,Zo,Z0=50.):
    if P==2:
        return TransresistanceAmplifierTwoPort(G,Zi,Zo,Z0=50.)
    elif P==3:
        return TransresistanceAmplifierThreePort(G,Zi,Zo,Z0=50.)
    elif P==4:
        return TransresistanceAmplifierFourPort(G,Zi,Zo,Z0=50.)

def TransresistanceAmplifierFourPort(G,Zi,Zo,Z0=50.):
    S11=Zi/(Zi+2.*Z0)
    S12=2.*Z0/(Zi+2.*Z0)
    S13=0
    S14=0
    S21=S12
    S22=S11
    S23=0
    S24=0
    S31=2.*G*Z0/((Zi+2.*Z0)*(Zo+2.*Z0))
    S32=-S31
    S33=Zo/(Zo+2.*Z0)
    S34=2.*Z0/(Zo+2.*Z0)
    S41=S32
    S42=S31
    S43=S34
    S44=S33
    return [[S11,S12,S13,S14],
            [S21,S22,S23,S24],
            [S31,S32,S33,S34],
            [S41,S42,S43,S44]]

def TransresistanceAmplifierThreePort(G,Zi,Zo,Z0=50.):
    return None

def TransresistanceAmplifierTwoPort(G,Zi,Zo,Z0=50.):
    return None

