class SubCircuit(SParameters):
    def __init__(self,f,fileName,args):
        sspnp=SystemSParametersNumericParser(f,args).File(fileName)
        SParameters.__init__(self,f,sspnp.SParameters())