class FractionalDelayFilterSinX(FirFilter):
    def __init__(self,F,accountForDelay=True):
        S=64
        U=1
        FirFilter.__init__(self,
            FilterDescriptor(U,S+F if accountForDelay else S,2*S),
            [SinXFunc(k,S,U,F) for k in range(2*U*S+1)])

