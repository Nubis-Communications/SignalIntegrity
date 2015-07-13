class TransferMatrices(object):
    def __init__(self,f,d):
        self.f=FrequencyList(f)
        self.Matrices=d
        self.Inputs=len(d[0][0])
        self.Outputs=len(d[0])
    def SParameters(self):
        from SignalIntegrity.SParameters.SParameters import SParameters
        if self.Inputs == self.Outputs:
            return SParameters(self.f,self.Matrices)
        else:
            squareMatrices=[]
            P=max(self.Inputs,self.Outputs)
            for transferMatrix in self.Matrices:
                squareMatrix=zeros((P,P),complex).tolist()
                for r in range(len(transferMatrix)):
                    for c in range(len(transferMatrix[0])):
                        squareMatrix[r][c]=transferMatrix[r][c]
                squareMatrices.append(squareMatrix)
            return SParameters(self.f,squareMatrices)
    def __len__(self):
        return len(self.f)
    def __getitem__(self,item):
        return self.Matrices[item]
...
