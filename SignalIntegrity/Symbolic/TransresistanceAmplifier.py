def TransresistanceAmplifier(P,G,Zi,Zo):
    if P==2:
        return TransresistanceAmplifierTwoPort(G,Zi,Zo)
    elif P==3:
        return TransresistanceAmplifierThreePort(G,Zi,Zo)
    elif P==4:
        return TransresistanceAmplifierFourPort(G,Zi,Zo)

def TransresistanceAmplifierFourPort(G,Zi,Zo):
    D11='\\frac{'+Zi+'}{'+Zi+'+2\\cdot Z0}'
    D12='\\frac{2\\cdot Z0}{'+Zi+'+2\\cdot Z0}'
    D31='\\frac{2\\cdot '+G+'\\cdot Z0}{\\left('+Zo+'+2\\cdot Z0\\right)\\cdot\\left('+Zi+'+2\\cdot Z0\\right)}'
    D33='\\frac{'+Zo+'}{'+Zo+'+2\\cdot Z0}'
    D34='\\frac{2\\cdot Z0}{'+Zo+'+2\\cdot Z0}'
    return [[D11,D12,'0','0'],
            [D12,D11,'0','0'] ,
            [D31,'-'+D31,D33,D34],
            ['-'+D31,D31,D34,D33]]
    
def TransresistanceAmplifierThreePort(G,Zi,Zo):
    D='3\\cdot Z0^2+\\left(2\\cdot '+Zo+'+2\\cdot '+Zi+'-'+G+'\\right)\\cdot Z0+'+Zo+'\\cdot '+Zi
    S11='\\frac{'+Zo+'\\cdot '+Zi+'+Z0\\cdot \\left(2\\cdot '+Zi+'-'+G+'\\right)-Z0^2}{'+D+'}'
    S12='\\frac{2\\cdot Z0^2}{'+D+'}'
    S13='\\frac{2\\cdot Z0^2+2\\cdot '+Zo+'\\cdot Z0}{'+D+'}'
    S21='\\frac{2\\cdot Z0^2+2\\cdot '+G+'\\cdot Z0}{'+D+'}'
    S22='\\frac{'+Zo+'\\cdot '+Zi+'+Z0\\cdot \\left(2\\cdot '+Zo+'-'+G+'\\right)-Z0^2}{'+D+'}'
    S23='\\frac{2\\cdot Z0^2+Z0\\cdot \\left(2\\cdot '+Zi+'-2\\cdot '+G+'\\right)}{'+D+'}'
    S31='\\frac{2\\cdot Z0^2+Z0\\cdot \\left(2\\cdot '+Zo+'-2\\cdot '+G+'\\right)}{'+D+'}'
    S32='\\frac{2\\cdot Z0^2+2\\cdot '+Zi+'\\cdot Z0}{'+D+'}'
    S33='\\frac{'+Zo+'\\cdot '+Zi+'-Z0^2+'+G+'\\cdot Z0}{'+D+'}'
    return [[S11,S12,S13],
            [S21,S22,S23],
            [S31,S32,S33]]

def TransresistanceAmplifierTwoPort(G,Zi,Zo):
    return [['\\frac{'+Zi+' - Z0}{'+Zi+' + Z0}','0'],
            ['\\frac{2\\cdot '+G+' \\cdot Z0}{\\left( '+Zi+' +Z0\\right)\\cdot\\left( '+Zo+' + Z0\\right)}','\\frac{'+Zo+' - Z0}{'+Zo+' + Z0}']]
