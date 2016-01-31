class FractionalDelayFilterLinear(FirFilter):
    def __init__(self,F,accountForDelay=True):
        from FilterDescriptor import FilterDescriptor
        FirFilter.__init__(self,FilterDescriptor(1,
            F if accountForDelay else 0,1),[1-F,F])

