class ErrorTerms(object):
...
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
...
