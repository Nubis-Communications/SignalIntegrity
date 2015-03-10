def CurrentAmplifier(P,G,Zi,Zo):
    if P==2:
        return CurrentAmplifierTwoPort(G,Zi,Zo)
    elif P==3:
        return CurrentAmplifierThreePort(G,Zi,Zo)
    elif P==4:
        return CurrentAmplifierFourPort(G,Zi,Zo)

def CurrentAmplifierFourPort(G,Zi,Zo):
    return [['\\frac{'+Zi+'}{'+Zi+'+2\\cdot Z0}','\\frac{2\\cdot Z0}{'+Zi+'+2\\cdot Z0}','0','0'],
            ['\\frac{2\\cdot Z0}{'+Zi+'+2\\cdot Z0}','\\frac{'+Zi+'}{'+Zi+'+2\\cdot Z0}','0','0'],
            ['\\frac{2\\cdot '+Zo+'\\cdot Z0\\cdot '+G+'}{\\left('+Zi+'+2\\cdot Z0\\right)\\cdot\left('+Zo+'+2\\cdot Z0\\right)}',
            '-\\frac{2\\cdot '+Zo+'\\cdot Z0\\cdot '+G+'}{\\left('+Zi+'+2\\cdot Z0\\right)\\cdot\\left('+Zo+'+2\\cdot Z0\\right)}',
            '\\frac{'+Zo+'}{'+Zo+'+2\\cdot Z0}','\\frac{2\\cdot Z0}{'+Zo+'+2\\cdot Z0}'],
            ['-\\frac{2\\cdot '+Zo+'\\cdot Z0\\cdot '+G+'}{\\left('+Zi+'+2\\cdot Z0\\right)\\cdot\\left('+Zo+'+2\\cdot Z0\\right)}',
            '\\frac{2\\cdot '+Zo+'\\cdot Z0\\cdot '+G+'}{\\left('+Zi+'+2\\cdot Z0\\right)\\cdot\\left('+Zo+'+2\\cdot Z0\\right)}',
            '\\frac{2\\cdot Z0}{'+Zo+'+2\\cdot Z0}','\\frac{'+Zo+'}{'+Zo+'+2\\cdot Z0}']]

def CurrentAmplifierThreePort(G,Zi,Zo):
    D='3\\cdot Z0^2+\\left(2\\cdot '+Zo+'+2\\cdot '+Zi+'-'+G+'\\cdot '+Zo+'\\right)\\cdot Z0+'+Zo+'\\cdot '+Zi
    S11='\\frac{'+Zo+'\\cdot '+Zi+'+Z0\\cdot \\left(2\\cdot '+Zi+'-'+G+'\\cdot '+Zo+'\\right)-Z0^2}{'+D+'}'
    S12='\\frac{2\\cdot Z0^2}{'+D+'}'
    S13='\\frac{2\\cdot Z0^2+2\\cdot '+Zo+'\\cdot Z0}{'+D+'}'
    S21='\\frac{2\\cdot Z0^2+2\\cdot '+G+'\\cdot '+Zo+'\\cdot Z0}{'+D+'}'
    S22='\\frac{'+Zo+'\\cdot '+Zi+'+Z0\\cdot \\left(2\\cdot '+Zo+'-'+G+'\\cdot '+Zo+'\\right)-Z0^2}{'+D+'}'
    S23='\\frac{2\\cdot Z0^2+Z0\\cdot \\left(2\\cdot '+Zi+'-2\\cdot '+G+'\\cdot '+Zo+'\\right)}{'+D+'}'
    S31='\\frac{2\\cdot Z0^2+Z0\\cdot \\left(2\\cdot '+Zo+'-2\\cdot '+G+'\\cdot '+Zo+'\\right)}{'+D+'}'
    S32='\\frac{2\\cdot Z0^2+2\\cdot '+Zi+'\\cdot Z0}{'+D+'}'
    S33='\\frac{'+Zo+'\\cdot '+Zi+'-Z0^2+'+G+'\\cdot '+Zo+'\\cdot Z0}{'+D+'}'
    return [[S11,S12,S13],
            [S21,S22,S23],
            [S31,S32,S33]]

def CurrentAmplifierTwoPort(G,Zi,Zo):
    return [['\\frac{'+Zi+' - Z0}{'+Zi+' + Z0}','0'],
            ['\\frac{2\\cdot '+G+' \\cdot '+Zo+' \\cdot Z0}{\\left( '+Zi+' +Z0\\right)\\cdot\\left( '+Zo+' + Z0\\right)}','\\frac{'+Zo+' - Z0}{'+Zo+' + Z0}']]
