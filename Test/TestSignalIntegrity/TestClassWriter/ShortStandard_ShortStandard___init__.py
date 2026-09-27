class ShortStandard(SParameters):
    def __init__(self,f,offsetDelay=0.0,offsetZ0=50.0,offsetLoss=0.0,f0=1e9,
                 L0=0.0,L1=0.0,L2=0.0,L3=0.0,Z0=50.):
        sspn=SystemSParametersNumeric(SystemDescriptionParser().AddLines(
            ['device offset 2','device L 1','port 1 offset 1','connect offset 2 L 1']
            ).SystemDescription())
        offsetSParameters=Offset(f,offsetDelay,offsetZ0,offsetLoss,f0,Z0=Z0)
        terminationSParameters=TerminationLPolynomial(f,L0,L1,L2,L3,Z0=Z0)
        sp=[]
        for n in range(len(f)):
            sspn.AssignSParameters('offset',offsetSParameters[n])
            sspn.AssignSParameters('L',terminationSParameters[n])
            sp.append(sspn.SParameters())
        SParameters.__init__(self,f,sp,Z0)