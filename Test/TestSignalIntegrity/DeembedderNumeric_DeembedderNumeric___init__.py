class DeembedderNumeric(Deembedder,Numeric):
    def __init__(self,sd=None):
        Deembedder.__init__(self,sd)
    def CalculateUnknown(self,Sk):
        Bmsd=self.PortANames()
        Amsd=self.PortBNames()
        Adut=self.DutANames()
        Bdut=self.DutBNames()
        Internals=self.OtherNames(Bmsd+Amsd+Adut+Bdut)
        G14=-array(self.WeightsMatrix(Bmsd,Amsd))
        G15=-array(self.WeightsMatrix(Bmsd,Bdut))
        G24=-array(self.WeightsMatrix(Adut,Amsd))
        G25=-array(self.WeightsMatrix(Adut,Bdut))
        if len(Internals)>0:# internal nodes
            G13=-array(self.WeightsMatrix(Bmsd,Internals))
            G23=-array(self.WeightsMatrix(Adut,Internals))
            G33=array(identity(len(Internals)))-\
                array(self.WeightsMatrix(Internals,Internals))
            G34=-array(self.WeightsMatrix(Internals,Amsd))
            G35=-array(self.WeightsMatrix(Internals,Bdut))
            F11=self.Dagger(G33,Left=G13,Right=G34,Mul=True)-G14
            F12=self.Dagger(G33,Left=G13,Right=G35,Mul=True)-G15
            F21=self.Dagger(G33,Left=G23,Right=G34,Mul=True)-G24
            F22=self.Dagger(G33,Left=G23,Right=G35,Mul=True)-G25
        else:# no internal nodes
            F11=-G14; F12=-G15; F21=-G24; F22=-G25
        #if long and skinny F12 then
        #F12.getI()=(F12.transpose()*F12).getI()*F12.transpose()
        #if short and fat F12, F12.getI() is wrong
        B=self.Dagger(F12,Right=(Sk-F11),Mul=True)
        A=F21+F22.dot(B)
        AL=self.Partition(A)# partition for multiple unknown devices
        BL=self.Partition(B)
        Su=[self.Dagger(AL[u],Left=BL[u],Mul=True).tolist() for u in range(len(AL))]
        if (len(Su)==1): return Su[0]# return the one result, not as a list
        return Su# return the list of results
