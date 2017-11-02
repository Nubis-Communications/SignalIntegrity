'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
from numpy import matrix,zeros

# Error terms are, for P ports, a P x P matrix of lists of three error terms.
# For the diagonal elements, the three error terms are ED, ER, and ES in that order
# for the off diagonal elements, the three error terms are EX, ET and EL in that order
# for r in 0...P-1, and c in 0...P-1,  ET[r][c] = [ED[r],ER[r],ES[r]], when r==c
# ET[r][c]=[EX[r][c],ET[r][c],EL[r][c]] when r !=c
class ErrorTerms(object):
    def __init__(self,ET=None):
        self.ET=ET
        if not ET is None:
            self.numPorts=len(ET)
        else:
            self.numPorts=None
    def Initialize(self,numPorts):
        self.numPorts=numPorts
        self.ET=[[[0.,0.,0.] for _ in range(self.numPorts)] for _ in range(self.numPorts)]
    def _Zeros(self):
        return [[0. for _ in range(self.numPorts)] for _ in range(self.numPorts)]
    def Fixture(self,m):
        E=[[self._Zeros(),self._Zeros()],[self._Zeros(),self._Zeros()]]
        for n in range(self.numPorts):
            ETn=self.ET[m][n]
            E[0][0][m][n]=ETn[0]
            E[0][1][n][n]=ETn[1]
            E[1][1][n][n]=ETn[2]
        E[1][0][m][m]=1.
        return E
    def ReflectCalibration(self,hatGamma,Gamma,m):
        A=[[1.,Gamma[r]*hatGamma[r],-Gamma[r]] for r in range(len(Gamma))]
        B=[[hatGamma[r]] for r in range(len(Gamma))]
        EdEsDeltaS=(matrix(B)*matrix(A).getI()).tolist()
        Ed=EdEsDeltaS[0][0]
        Es=EdEsDeltaS[1][0]
        DeltaS=EdEsDeltaS[2][0]
        Er=DeltaS-Ed*Es
        self.ET[m][m]=[Ed,Er,Es]
        return self
    def ThruCalibration(self,b1a1,b2a1,S,m,n):
        [Ed,Er,Es]=self.ET[m][m]
        Ex=self.ET[m][n][0]
        A=zeros((2*len(b1a1),2)).tolist()
        B=zeros((2*len(b1a1),1)).tolist
        for i in range(len(b1a1)):
            Sm=S[i]
            detS=matrix(Sm).det()
            A[2*i][0]=(Es*detS-Sm[1][1])*(Ed-b1a1[i])-Er*detS
            A[2*i][1]=0.
            A[2*i+1][0]=(Es*detS-Sm[1][1])*(Ex-b2a1[i])
            A[2*i+1][1]=Sm[1][0]
            B[2*i][0]=(1.-Es*Sm[0][0])*(b1a1[i]-Ed)-Er*Sm[0][0]
            B[2*i+1][0]=(1-Es*Sm[0][0])*(b2a1[i]-Ex)
        [El,Et]=(matrix(B)*matrix(A).getI()).tolist()
        self.ET[m][n]=[Ex,Et,El]
        return self
    def ExCalibration(self,b2a1,m,n):
        [Ex,Et,El]=self.ET[m][n]
        Ex=b2a1
        self.ET[m][n]=[Ex,Et,El]
        return self
    
    
