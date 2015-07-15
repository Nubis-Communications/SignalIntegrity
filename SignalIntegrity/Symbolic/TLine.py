def TLine(P,Zc,gamma):
    if P==2:
        return TLineTwoPort(Zc,gamma)
    elif P==4:
        return TLineFourPort(Zc,gamma)

def TLineFourPort(Zc,gamma):
    pass

def TLineTwoPort(Zc,gamma):
    p='\\frac{\\left('+Zc+'-Z0\\right)}{\\left('+Zc+'+Z0\\right)}'
    L='e^{-'+gamma+'}'
    L2='e^{-2\cdot '+gamma+'}'
    D='1-\\left['+p+'\\right]^2\\cdot '+L2
    S1='\\frac{\\left['+p+'\\cdot\\left(1-'+L2+'\\right)\\right]}{'+D+'}'
    S2='\\frac{\\left['+L+'\\cdot\\left(1-\\left['+p+'\\right]^2\\right]}{'+D+'}'
    return [[S1,S2],[S2,S1]]