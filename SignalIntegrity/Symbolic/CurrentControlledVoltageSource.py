def CurrentControlledVoltageSource(G):
    return  [['0','1','0','0'],
             ['1','0','0','0'],
             ['-\\frac{'+G+' }{2\\cdot Z0}','\\frac{'+G+' }{2\\cdot Z0}','0','1'],
             ['\\frac{'+G+' }{2\\cdot Z0}','-\\frac{'+G+' }{2\\cdot Z0}','1','0']]
