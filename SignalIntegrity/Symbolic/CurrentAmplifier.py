def CurrentAmplifierFourPort(G,Zi,Zo):
    return [['\\frac{'+Zi+'}{'+Zi+'+2\\cdot Z0}','\\frac{2\\cdot Z0}{'+Zi+'+2\\cdot Z0}','0','0'],
            ['\\frac{2\\cdot Z0}{'+Zi+'+2\\cdot Z0}','\\frac{'+Zi+'}{'+Zi+'+2\\cdot Z0}','0','0'],
            ['\\frac{2\\cdot '+Zo+'\\cdot Z0\\cdot '+G+'}{\\left('+Zi+'+2\\cdot Z0\\right)\\cdot\left('+Zo+'+2\\cdot Z0\\right)}',
            '-\\frac{2\\cdot '+Zo+'\\cdot Z0\\cdot '+G+'}{\\left('+Zi+'+2\\cdot Z0\\right)\\cdot\\left('+Zo+'+2\\cdot Z0\\right)}',
            '\\frac{'+Zo+'}{'+Zo+'+2\\cdot Z0}','\\frac{2\\cdot Z0}{'+Zo+'+2\\cdot Z0}'],
            ['-\\frac{2\\cdot '+Zo+'\\cdot Z0\\cdot '+G+'}{\\left('+Zi+'+2\\cdot Z0\\right)\\cdot\\left('+Zo+'+2\\cdot Z0\\right)}',
            '\\frac{2\\cdot '+Zo+'\\cdot Z0\\cdot '+G+'}{\\left('+Zi+'+2\\cdot Z0\\right)\\cdot\\left('+Zo+'+2\\cdot Z0\\right)}',
            '\\frac{2\\cdot Z0}{'+Zo+'+2\\cdot Z0}','\\frac{'+Zo+'}{'+Zo+'+2\\cdot Z0}']]
