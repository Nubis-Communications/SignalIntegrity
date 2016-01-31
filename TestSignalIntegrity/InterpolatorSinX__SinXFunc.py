def SinXFunc(k,S,U,F):
    if float(k)/U-F-S==0:
        return 1.
    else:
        return math.sin(math.pi*(float(k)/U-F-S))/(math.pi*(float(k)/U-F-S))*\
            (1./2.+1./2.*math.cos(math.pi*(float(k)/U-S)/S))

