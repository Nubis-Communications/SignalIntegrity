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
...
