class ThruStandard(SParameters):
    def __init__(self,f,offsetDelay=0.0,offsetZ0=50.0,offsetLoss=0.0,f0=1e9):
        SParameters.__init__(self,f,Offset(f,offsetDelay,offsetZ0,offsetLoss,f0).m_d)
