class ErrorTerms(object):
    def __init__(self,ET=None):
        self.ET=ET
        if not ET is None:
            self.numPorts=len(ET)
        else:
            self.numPorts=None
    def Initialize(self,numPorts):
        self.numPorts=numPorts
        self.ET=[[[0.,0.,0.] for _ in range(self.numPorts)]
                 for _ in range(self.numPorts)]
        return self
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
    def ThruCalibration(self,b1a1,b2a1,S,n,m):
        [Ed,Er,Es]=self[m][m]
        Ex=self[n][m][0]
        A=zeros((2*len(b1a1),2)).tolist()
        B=zeros((2*len(b1a1),1)).tolist()
        for i in range(len(b1a1)):
            Sm=S[i]
            detS=det(matrix(Sm))
            A[2*i][0]=(Es*detS-Sm[1][1])*(Ed-b1a1[i])-Er*detS
            A[2*i][1]=0.
            A[2*i+1][0]=(Es*detS-Sm[1][1])*(Ex-b2a1[i])
            A[2*i+1][1]=Sm[1][0]
            B[2*i][0]=(1.-Es*Sm[0][0])*(b1a1[i]-Ed)-Er*Sm[0][0]
            B[2*i+1][0]=(1-Es*Sm[0][0])*(b2a1[i]-Ex)
        ElEt=(matrix(A).getI()*matrix(B)).tolist()
        (El,Et)=(ElEt[0][0],ElEt[1][0])
        self[n][m]=[Ex,Et,El]
        return self
    def ExCalibration(self,b2a1,n,m):
        [Ex,Et,El]=self[n][m]
        Ex=b2a1
        self[n][m]=[Ex,Et,El]
        return self
    def TransferThruCalibration(self):
        for otherPort in range(self.numPorts):
            for drivenPort in range(self.numPorts):
                if (otherPort != drivenPort):
                    if all(self[otherPort][drivenPort][1:])==0.:
                        for mid in range(self.numPorts):
                            if all(self[otherPort][drivenPort][1:])==0.:
                                if ((mid != otherPort) and
                                    (mid != drivenPort) and
                                    (any(self[otherPort][mid][1:])!=0.) and
                                    (any(self[mid][drivenPort][1:])!=0.)):
                                    (Exl,Etl,Ell)=self[otherPort][mid]
                                    (Exr,Etr,Elr)=self[mid][drivenPort]
                                    (Edm,Erm,Esm)=self[mid][mid]
                                    (Edo,Ero,Eso)=self[otherPort][otherPort]
                                    (Ex,Et,El)=self[otherPort][drivenPort]
                                    Et=Etl*Etr/Erm
                                    El=Eso
                                    self[otherPort][drivenPort]=[Ex,Et,El]
        return self
...
