def ShuntZTwoPort(Z,Z0=50.):
    D=(Z0+2.*Z)
    return [[-Z0/D,2.*Z/D],
        [2.*Z/D,-Z0/D]]
