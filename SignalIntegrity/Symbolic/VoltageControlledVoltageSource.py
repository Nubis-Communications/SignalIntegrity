def VoltageControlledVoltageSource(G):
    return  [['1','0','0','0'],
            ['0','1','0','0'],
            [G,'-'+G,'0','1'],
            ['-'+G,G,'1','0']]
