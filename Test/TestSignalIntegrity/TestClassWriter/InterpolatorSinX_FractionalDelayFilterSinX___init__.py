class FractionalDelayFilterSinX(FirFilter):
    def __init__(self,F,accountForDelay=True):
        U=1
        FirFilter.__init__(self,
            FilterDescriptor(U,self.S+F if accountForDelay else self.S,2*self.S),
                SinX(self.S,U,F))

