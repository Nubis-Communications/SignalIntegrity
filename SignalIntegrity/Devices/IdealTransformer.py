def IdealTransformer(a=1.):
    a=float(a)
    D=a*a+1.
    return [[1./D,a*a/D,a/D,-a/D],
            [a*a/D,1./D,-a/D,a/D],
            [a/D,-a/D,a*a/D,1./D],
            [-a/D,a/D,1./D,a*a/D]]
