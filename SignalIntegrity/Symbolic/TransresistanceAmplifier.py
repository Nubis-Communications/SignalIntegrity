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