class LoadStandard(SParameters):
    def __init__(self,f,offsetDelay=0.0,offsetZ0=50.0,offsetLoss=0.0,
                 terminationZ0=50.0):
        sd=SystemDescription()
        sd.AddDevice('offset',2)
        sd.AddDevice('Z',1)
        sd.AddPort('offset',1,1)
        sd.ConnectDevicePort('offset',2,'Z',1)
        sspn=SystemSParametersNumeric(sd)
        offsetSParameters=Offset(f,offsetDelay,offsetZ0,offsetLoss)
        terminationSParameters=TerminationZ(terminationZ0)
        sp=[]
        for n in range(len(f)):
            sspn.AssignSParameters('offset',offsetSParameters[n])
            sspn.AssignSParameters('Z',terminationSParameters)
            sp.append(sspn.SParameters())
        SParameters.__init__(self,f,sp)
