class ErrorTerms(object):
...
    def ReflectCalibration(self,hatGamma,Gamma,m):
        A=[[1.,Gamma[r]*hatGamma[r],-Gamma[r]] for r in range(len(Gamma))]
        B=[[hatGamma[r]] for r in range(len(Gamma))]
        EdEsDeltaS=(matrix(A).getI()*matrix(B)).tolist()
        Ed=EdEsDeltaS[0][0]
        Es=EdEsDeltaS[1][0]
        DeltaS=EdEsDeltaS[2][0]
        Er=Ed*Es-DeltaS
        self[m][m]=[Ed,Er,Es]
        return self
...
