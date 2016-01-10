def ShuntZTwoPort(Z,Z0=50.):
    return [[-Z0*Z0/(Z0*Z0+2.*Z*Z0),2.*Z0*Z/(Z0*Z0+2.*Z*Z0)],
        [2.*Z0*Z/(Z0*Z0+2.*Z*Z0),-Z0*Z0/(Z0*Z0+2.*Z*Z0)]]
