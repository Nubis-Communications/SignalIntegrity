def VoltageControlledCurrentSource(G,Z0=50):
    return  [[1.,0.,0.,0.],
            [0.,1.,0.,0.],
            [2.*G*Z0,-2.*G*Z0,1.,0.],
            [-2.*G*Z0,2.*G*Z0,0.,1.]]