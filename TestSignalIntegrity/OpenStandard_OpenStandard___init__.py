class OpenStandard(SParameters):
    def __init__(self,f,offsetDelay=0.0,offsetZ0=50.0,offsetLoss=0.0,
                 C0=0.0,C1=0.0,C2=0.0,C3=0.0):
        sspn=SystemSParametersNumeric(SystemDescriptionParser().AddLines(
            ['device offset 2','device C 1','port 1 offset 1','connect offset 2 C 1']
            ).SystemDescription())
        offsetSParameters=Offset(f,offsetDelay,offsetZ0,offsetLoss)
        terminationSParameters=TerminationCPolynomial(f,C0,C1,C2,C3)
        sp=[]
        for n in range(len(f)):
            sspn.AssignSParameters('offset',offsetSParameters[n])
            sspn.AssignSParameters('C',terminationSParameters[n])
            sp.append(sspn.SParameters())
        SParameters.__init__(self,f,sp)
