class SubCircuit(SParameters):
    def __init__(self,f,fileName,args,Z0=50.):
        sspnp=SystemSParametersNumericParser(f,args,Z0=Z0).File(fileName)
        SParameters.__init__(self,f,sspnp.SParameters())
