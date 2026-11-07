class ThruStandard(Offset):
    def __init__(self,f,offsetDelay=0.0,offsetZ0=50.0,offsetLoss=0.0,f0=1e9,Z0=50.):
        Offset.__init__(self,f,offsetDelay,offsetZ0,offsetLoss,f0,Z0=50.)
