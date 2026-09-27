class Deembedder(SystemSParameters):
    def __init__(self,sd=None):
        SystemSParameters.__init__(self,sd)
    def AddUnknown(self,Name,Ports):
        self.AddDevice(Name,Ports,SParams=None,Type='unknown')
    def DutANames(self):
        return [p.A for d in self for p in d if d.Type=='unknown']
    def DutBNames(self):
        return [p.B for d in self for p in d if d.Type=='unknown']
    def UnknownNames(self):
        return [d.Name for d in self if d.Type=='unknown']
    def UnknownPorts(self):
        return [len(d) for d in self if d.Type=='unknown']
    def Partition(self,A):#a list of arrays, one per unknown device
        PL=self.UnknownPorts()
        Result=[]
        S=0
        for d in range(len(PL)):
            Result.append(A[S:S+PL[d],])
            S=S+PL[d]
        return Result