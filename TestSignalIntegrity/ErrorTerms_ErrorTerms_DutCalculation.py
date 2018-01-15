class ErrorTerms(object):
...
    def Fixture(self,m):
        E=[[zeros((self.numPorts,self.numPorts),complex).tolist(),
            zeros((self.numPorts,self.numPorts),complex).tolist()],
           [zeros((self.numPorts,self.numPorts),complex).tolist(),
            zeros((self.numPorts,self.numPorts),complex).tolist()]]
        for n in range(self.numPorts):
            ETn=self[n][m]
            E[0][0][m][n]=ETn[0]
            E[0][1][n][n]=ETn[1]
            E[1][1][n][n]=ETn[2]
        E[1][0][m][m]=1.
        return E
    def DutCalculationAlternate(self,sRaw):
        if self.numPorts==1:
            (Ed,Er,Es)=self[0][0]
            gamma=sRaw[0][0]
            Gamma=(gamma-Ed)/((gamma-Ed)*Es+Er)
            return Gamma
        else:
            A=zeros((self.numPorts,self.numPorts),complex).tolist()
            B=zeros((self.numPorts,self.numPorts),complex).tolist()
            I=(identity(self.numPorts)).tolist()
            for m in range(self.numPorts):
                E=self.Fixture(m)
                b=matrix([[sRaw[r][m]] for r in range(self.numPorts)])
                Im=matrix([[I[r][m]] for r in range(self.numPorts)])
                bprime=(matrix(E[0][1]).getI()*(b-matrix(E[0][0])*Im)).tolist()
                aprime=(matrix(E[1][0])*Im+matrix(E[1][1])*matrix(bprime)).tolist()
                for r in range(self.numPorts):
                    A[r][m]=aprime[r][0]
                    B[r][m]=bprime[r][0]
            S=(matrix(B)*matrix(A).getI()).tolist()
            return S
    def DutCalculation(self,sRaw):
        B=[[(sRaw[r][c]-self[r][c][0])/self[r][c][1] for c in range(len(sRaw))]
           for r in  range(len(sRaw))]
        A=[[B[r][c]*self[r][c][2]+(1 if r==c else 0) for c in range(len(sRaw))]
           for r in range(len(sRaw))]
        S=(matrix(B)*matrix(A).getI()).tolist()
        return S
