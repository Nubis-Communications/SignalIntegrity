def CurrentControlledVoltageSource(G,Z0=50.):
    return  [[0.,1.,0.,0.],
            [1.,0.,0.,0.],
            [-G/(2.*Z0),G/(2.*Z0),0.,1.],
            [G/(2.*Z0),-G/(2.*Z0),1.,0.]]