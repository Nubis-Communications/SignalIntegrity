class ShortStandard(SParameters):
    def __init__(self,f,offsetDelay=0.0,offsetZ0=50.0,offsetLoss=0.0,
                 L0=0.0,L1=0.0,L2=0.0,L3=0.0):
        sd=SystemDescription()
        sd.AddDevice('offset',2)
        sd.AddDevice('L',1)
        sd.AddPort('offset',1,1)
        sd.ConnectDevicePort('offset',2,'L',1)
        sspn=SystemSParametersNumeric(sd)
        offsetSParameters=Offset(f,offsetDelay,offsetZ0,offsetLoss)
        terminationSParameters=TerminationLPolynomial(f,L0,L1,L2,L3)
        sp=[]
        for n in range(len(f)):
            sspn.AssignSParameters('offset',offsetSParameters[n])
            sspn.AssignSParameters('L',terminationSParameters[n])
            sp.append(sspn.SParameters())
        SParameters.__init__(self,f,sp)