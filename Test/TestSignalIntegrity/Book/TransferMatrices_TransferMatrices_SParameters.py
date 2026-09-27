class TransferMatrices(list,CallBacker):
    def __init__(self,f,d):
        self.f=FrequencyList(f)
        list.__init__(self,d)
        CallBacker.__init__(self)
        self.Inputs=len(d[0][0])
        self.Outputs=len(d[0])
        self.fr=None
        self.ir=None
        self.td=None
    def SParameters(self):
        if self.Inputs == self.Outputs:
            return SParameters(self.f,self)
        else:
            squareMatrices=[]
            P=max(self.Inputs,self.Outputs)
            for transferMatrix in self:
                squareMatrix=zeros((P,P),complex).tolist()
                for r in range(len(transferMatrix)):
                    for c in range(len(transferMatrix[0])):
                        squareMatrix[r][c]=transferMatrix[r][c]
                squareMatrices.append(squareMatrix)
            return SParameters(self.f,squareMatrices)
...
