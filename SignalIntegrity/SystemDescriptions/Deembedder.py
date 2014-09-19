from SystemSParameters import SystemSParameters

class Deembedder(SystemSParameters):
    def __init__(self,sd):
        self.Data = sd.Data
    def DutANames(self):
        return [p.pA for d in self for p in d if d.pName[0]=='?']
    def DutBNames(self):
        return [p.pB for d in self for p in d if d.pName[0]=='?']
    def UnknownNames(self):
        return [d.pName for d in self if d.pName[0]=='?']
    def UnknownPorts(self):
        return [len(d) for d in self if d.pName[0]=='?']
    def Partition(self,A):#a list of arrays, one per unknown device
        PL=self.UnknownPorts()
        Result=[]
        S=0
        for d in range(len(PL)):
            Result.append(A[S:S+PL[d],])
            S=S+PL[d]
        return Result