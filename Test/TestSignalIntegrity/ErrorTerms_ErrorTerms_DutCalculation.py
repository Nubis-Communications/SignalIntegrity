class ErrorTerms(object):
...
    def Fixture(self,m,pl=None):
        if pl is None: pl = [p for p in range(self.numPorts)]
        numPorts=len(pl)
        E=[[zeros((numPorts,numPorts),complex).tolist(),
            zeros((numPorts,numPorts),complex).tolist()],
           [zeros((numPorts,numPorts),complex).tolist(),
            zeros((numPorts,numPorts),complex).tolist()]]
        for n in range(numPorts):
            ETn=self[pl[n]][pl[m]]
            E[0][0][m][n]=ETn[0]
            E[0][1][n][n]=ETn[1]
            E[1][1][n][n]=ETn[2]
        E[1][0][m][m]=1.
        return E
    def DutCalculationAlternate(self,sRaw,pl=None):
        if pl is None: pl = [p for p in range(len(sRaw))]
        numPorts=len(pl)
        if numPorts==1:
            (Ed,Er,Es)=self[pl[0]][pl[0]]
            gamma=sRaw[0][0]
            Gamma=(gamma-Ed)/((gamma-Ed)*Es+Er)
            return [[Gamma]]
        else:
            A=zeros((numPorts,numPorts),complex).tolist()
            B=zeros((numPorts,numPorts),complex).tolist()
            I=(identity(numPorts)).tolist()
            for m in range(numPorts):
                E=self.Fixture(m,pl)
                b=matrix([[sRaw[r][m]] for r in range(numPorts)])
                Im=matrix([[I[r][m]] for r in range(numPorts)])
                bprime=(matrix(E[0][1]).getI()*(b-matrix(E[0][0])*Im)).tolist()
                aprime=(matrix(E[1][0])*Im+matrix(E[1][1])*matrix(bprime)).tolist()
                for r in range(numPorts):
                    A[r][m]=aprime[r][0]
                    B[r][m]=bprime[r][0]
            S=(matrix(B)*matrix(A).getI()).tolist()
            return S
    def DutCalculation(self,sRaw,pl=None):
        if pl is None: pl = [p for p in range(len(sRaw))]
        B=[[(sRaw[r][c]-self[pl[r]][pl[c]][0])/self[pl[r]][pl[c]][1]
            for c in range(len(sRaw))] for r in  range(len(sRaw))]
        A=[[B[r][c]*self[pl[r]][pl[c]][2]+(1 if r==c else 0) for c in range(len(sRaw))]
           for r in range(len(sRaw))]
        S=(matrix(B)*matrix(A).getI()).tolist()
        return S