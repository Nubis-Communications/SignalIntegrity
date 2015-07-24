from SignalIntegrity.SParameters import SParameters

class SubCircuit(SParameters):
    def __init__(self,f,fileName,args):
        from SignalIntegrity.Parsers import SystemSParametersNumericParser
        sspnp=SystemSParametersNumericParser(f,args).File(fileName)
        SParameters.__init__(self,f,sspnp.SParameters().Data())