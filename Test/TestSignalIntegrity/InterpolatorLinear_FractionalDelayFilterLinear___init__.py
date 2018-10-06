class FractionalDelayFilterLinear(FirFilter):
    def __init__(self,F,accountForDelay=True):
        FirFilter.__init__(self,FilterDescriptor(1,
            (F if F >= 0 else 1+F) if accountForDelay else 0,1),
            [1-F,F] if F >= 0 else [-F,1+F])

