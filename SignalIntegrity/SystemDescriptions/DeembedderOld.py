from numpy import matrix
from numpy import array
from numpy import identity

from SignalIntegrity.SystemDescriptions import SystemDescription
from SignalIntegrity.SystemDescriptions import SystemSParametersCalculator

class Deembedder(SystemDescription):
    def __init__(self,sd):
        self.Data = sd.Data
    def DutANames(self):
        return [self[d][p].A() for d in range(len(self))
                for p in range(len(self[d])) if self[d].Name()[0]=='?']
    def DutBNames(self):
        return [self[d][p].B() for d in range(len(self))
                for p in range(len(self[d])) if self[d].Name()[0]=='?']
    def UnknownNames(self):
        return [self[d].Name() for d in range(len(self)) if self[d].Name()[0]=='?']
    def UnknownPorts(self):
        return [len(self[d]) for d in range(len(self)) if self[d].Name()[0]=='?']
    def Partition(self,A):#a list of arrays, one per unknown device
        PL=self.UnknownPorts()
        Result=[]
        S=0
        for d in range(len(PL)):
            Result.append(A[S:S+PL[d],])
            S=S+PL[d]
        return Result
    def Unknown(self,Sk):
        SC=SystemSParametersCalculator(self)
        Bmsd=SC.PortANames()
        Amsd=SC.PortBNames()
        A=self.DutANames()
        B=self.DutBNames()
        U=SC.OtherNames(Bmsd+Amsd+A+B)
        G14=-matrix(SC.WeightsMatrix(Bmsd,Amsd))
        G15=-matrix(SC.WeightsMatrix(Bmsd,B))
        G24=-matrix(SC.WeightsMatrix(A,Amsd))
        G25=-matrix(SC.WeightsMatrix(A,B))
        if len(U)>0: 
            G13=-matrix(SC.WeightsMatrix(Bmsd,U))
            G23=-matrix(SC.WeightsMatrix(A,U))
            G33=matrix(identity(len(U)))-matrix(SC.WeightsMatrix(U,U))
            G34=-matrix(SC.WeightsMatrix(U,Amsd))
            G35=-matrix(SC.WeightsMatrix(U,B))
            B=(G13*G33.getI()*G35-G15).getI()*(Sk-(G13*G33.getI()*G34-G14))
            A=(G23*G33.getI()*G34-G24)+(G23*G33.getI()*G35-G25)*B
        else:
            B=(-G15).getI()*(Sk+G14)
            A=-G24-G25*B            
        Su=B*A.getI()
        return Su.tolist()
    def UnknownFixtureDeembedding(self,Sk):
        SC=SystemSParametersCalculator(self)
        Bmsd=SC.PortANames()
        Amsd=SC.PortBNames()
        A=self.DutANames()
        B=self.DutBNames()
        U=SC.OtherNames(Bmsd+Amsd+A+B)
        G14=-matrix(SC.WeightsMatrix(Bmsd,Amsd))
        G15=-matrix(SC.WeightsMatrix(Bmsd,B))
        G24=-matrix(SC.WeightsMatrix(A,Amsd))
        G25=-matrix(SC.WeightsMatrix(A,B))
        if len(U)>0: 
            G13=-matrix(SC.WeightsMatrix(Bmsd,U))
            G23=-matrix(SC.WeightsMatrix(A,U))
            G33I=(matrix(identity(len(U)))-matrix(SC.WeightsMatrix(U,U))).getI()
            G34=-matrix(SC.WeightsMatrix(U,Amsd))
            G35=-matrix(SC.WeightsMatrix(U,B))
            F11=G13*G33I*G34-G14
            F12=G13*G33I*G35-G15
            F21=G23*G33I*G34-G24
            F22=G23*G33I*G35-G25
        else:
            F11=-G14
            F12=-G15
            F21=-G24
            F22=-G25
        if len(Bmsd)>len(B):
            B=(F12.transpose()*F12).getI()*F12.transpose()*(Sk-F11)
            A=F21+F22*B
            Su=B*A.transpose()*(A*A.transpose()).getI()
        else:
            B=F12.getI()*(Sk-F11)
            A=F21+F22*B            
            Su=B*A.getI()
        return Su.tolist()
    def CalculateUnknown(self,Sk):
        SC=SystemSParametersCalculator(self)
        Bmsd=SC.PortANames()
        Amsd=SC.PortBNames()
        Adut=self.DutANames()
        Bdut=self.DutBNames()
        Internals=SC.OtherNames(Bmsd+Amsd+Adut+Bdut)
        G14=-matrix(SC.WeightsMatrix(Bmsd,Amsd))
        G15=-matrix(SC.WeightsMatrix(Bmsd,Bdut))
        G24=-matrix(SC.WeightsMatrix(Adut,Amsd))
        G25=-matrix(SC.WeightsMatrix(Adut,Bdut))
        if len(Internals)>0:# internal nodes
            G13=-matrix(SC.WeightsMatrix(Bmsd,Internals))
            G23=-matrix(SC.WeightsMatrix(Adut,Internals))
            G33I=(matrix(identity(len(Internals)))-matrix(SC.WeightsMatrix(Internals,Internals))).getI()
            G34=-matrix(SC.WeightsMatrix(Internals,Amsd))
            G35=-matrix(SC.WeightsMatrix(Internals,Bdut))
            F11=G13*G33I*G34-G14
            F12=G13*G33I*G35-G15
            F21=G23*G33I*G34-G24
            F22=G23*G33I*G35-G25
        else:# no internal nodes
            F11=-G14
            F12=-G15
            F21=-G24
            F22=-G25
        if F12.shape[0]>F12.shape[1]:# tall and skinny F12
            B=(F12.transpose()*F12).getI()*F12.transpose()*(Sk-F11)
            A=F21+F22*B
        else:# hopefully square F12
            B=F12.getI()*(Sk-F11)
            A=F21+F22*B
        AL=self.Partition(A)# partition for multiple unknown devices
        BL=self.Partition(B)
        Su=[]
        for u in range(len(AL)):# for each unknown device
            if AL[u].shape[0]<AL[u].shape[1]:# short and fat A
                Su.append((BL[u]*AL[u].transpose()*(AL[u]*AL[u].transpose()).getI()).tolist())
            else:# hopefully square A
                Su.append((BL[u]*AL[u].getI()).tolist())
        if (len(Su)==1):# only one result
            return Su[0]# return the one result, not as a list
        return Su# return the list of results
        
        
