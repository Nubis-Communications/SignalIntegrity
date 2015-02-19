def CurrentControlledCurrentSource(G):
    return  [[0.,1.,0.,0.],
            [1.,0.,0.,0.],
            [-G,G,1.,0.],
            [G,-G,0.,1.]]