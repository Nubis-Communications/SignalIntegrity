from SignalIntegrity.SParameters import SParameters

class SubCircuit(SParameters):
    def __init__(self,f,fileName,args):
        from SignalIntegrity.Parsers import SystemSParametersNumericParser
        SParameters.__init__(self,f,SystemSParametersNumericParser(f,args).File(fileName).SParameters().Data())

