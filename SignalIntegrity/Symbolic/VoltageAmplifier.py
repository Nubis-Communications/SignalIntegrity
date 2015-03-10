def VoltageAmplifier(P,G,Zi,Zo):
    if P==2:
        return VoltageAmplifierTwoPort(G,Zi,Zo)
    elif P==3:
        return VoltageAmplifierThreePort(G,Zi,Zo)
    elif P==4:
        return VoltageAmplifierFourPort(G,Zi,Zo)

def VoltageAmplifierFourPort(G,Zi,Zo):
    return [['\\frac{'+Zi+'}{'+Zi+'+2\\cdot Z0}','\\frac{2\\cdot Z0}{'+Zi+'+2\\cdot Z0}','0','0'],
            ['\\frac{2\\cdot Z0}{'+Zi+'+2\\cdot Z0}','\\frac{'+Zi+'}{'+Zi+'+2\\cdot Z0}','0','0'],
            ['\\frac{2\\cdot '+Zi+'\\cdot Z0\\cdot '+G+'}{\\left('+Zi+'+2\\cdot Z0\\right)\\cdot\left('+Zo+'+2\\cdot Z0\\right)}',
            '-\\frac{2\\cdot '+Zi+'\\cdot Z0\\cdot '+G+'}{\\left('+Zi+'+2\\cdot Z0\\right)\\cdot\\left('+Zo+'+2\\cdot Z0\\right)}',
            '\\frac{'+Zo+'}{'+Zo+'+2\\cdot Z0}','\\frac{2\\cdot Z0}{'+Zo+'+2\\cdot Z0}'],
            ['-\\frac{2\\cdot '+Zi+'\\cdot Z0\\cdot '+G+'}{\\left('+Zi+'+2\\cdot Z0\\right)\\cdot\\left('+Zo+'+2\\cdot Z0\\right)}',
            '\\frac{2\\cdot '+Zi+'\\cdot Z0\\cdot '+G+'}{\\left('+Zi+'+2\\cdot Z0\\right)\\cdot\\left('+Zo+'+2\\cdot Z0\\right)}',
            '\\frac{2\\cdot Z0}{'+Zo+'+2\\cdot Z0}','\\frac{'+Zo+'}{'+Zo+'+2\\cdot Z0}']]

def VoltageAmplifierThreePort(G,Zi,Zo):
    D='-'+Zo+'\\cdot '+Zi+'-2\\cdot '+Zo+'\\cdot Z0-2\\cdot '+Zi+'\\cdot Z0-3\\cdot Z0^2+'+G+'\\cdot '+Zi+'\\cdot Z0'
    S11='\\frac{-'+Zo+'\\cdot '+Zi+'-2\\cdot '+Zi+'\\cdot Z0+Z0^2+'+G+'\\cdot '+Zi+'\\cdot Z0}{'+D+'}'
    S12='\\frac{-2\\cdot Z0^2}{'+D+'}'
    S13='\\frac{-2\\cdot Z0\\cdot\\left('+Zo+' +Z0\\right)}{'+D+'}'
    S21='\\frac{-2\\cdot Z0 \\cdot\\left('+G+'\\cdot '+Zi+' +Z0\\right)}{'+D+'}'
    S22='\\frac{Z0^2-2\\cdot '+Zo+'\\cdot Z0+'+G+'\\cdot '+Zi+'\\cdot Z0-'+Zo+'\\cdot '+Zi+'}{'+D+'}'
    S23='\\frac{2\\cdot Z0\\cdot\\left('+G+'\\cdot '+Zi+'-'+Zi+'-Z0\\right)}{'+D+'}'
    S31='\\frac{2\\cdot Z0\\cdot\\left(-Z0+'+G+'\\cdot '+Zi+'-'+Zo+'\\right)}{'+D+'}'
    S32='\\frac{-2\\cdot Z0\\cdot\\left('+Zi+'+Z0\\right)}{'+D+'}'
    S33='\\frac{-'+Zo+'\\cdot '+Zi+'+Z0^2-'+G+'\\cdot '+Zi+'\\cdot Z0}{'+D+'}'
    return [[S11,S12,S13],
            [S21,S22,S23],
            [S31,S32,S33]]

def VoltageAmplifierTwoPort(G,Zi,Zo):
    return [['\\frac{'+Zi+' - Z0}{'+Zi+' + Z0}','0'],
            ['\\frac{2\\cdot '+G+' \\cdot '+Zi+' \\cdot Z0}{\\left( '+Zi+' +Z0\\right)\\cdot\\left( '+Zo+' + Z0\\right)}','\\frac{'+Zo+' - Z0}{'+Zo+' + Z0}']]
