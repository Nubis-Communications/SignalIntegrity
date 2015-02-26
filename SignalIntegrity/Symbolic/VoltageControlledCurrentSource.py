def VoltageControlledCurrentSource(G):
    return  [['1','0','0','0'],
            ['0','1','0','0'],
            ['2\\cdot '+G+' \\cdot Z0','-2\\cdot '+G+' \\cdot Z0','1','0'],
            ['-2\\cdot '+G+' \\cdot Z0','2\\cdot '+G+' \\cdot Z0','0','1']]
