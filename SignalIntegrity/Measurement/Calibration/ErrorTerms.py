'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
from numpy import matrix,zeros, identity
from numpy.linalg import det

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
        return self
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
        EdEsDeltaS=(matrix(A).getI()*matrix(B)).tolist()
        Ed=EdEsDeltaS[0][0]
        Es=EdEsDeltaS[1][0]
        DeltaS=EdEsDeltaS[2][0]
        Er=Ed*Es-DeltaS
        self.ET[m][m]=[Ed,Er,Es]
        return self
    def ThruCalibration(self,b1a1,b2a1,S,m,n):
        if not isinstance(b1a1,list):
            b1a1=[b1a1]
            b2a1=[b2a1]
            S=[S]
        [Ed,Er,Es]=self.ET[m][m]
        Ex=self.ET[m][n][0]
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
        self.ET[m][n]=[Ex,Et,El]
        return self
    def ExCalibration(self,b2a1,m,n):
        [Ex,Et,El]=self.ET[m][n]
        Ex=b2a1
        self.ET[m][n]=[Ex,Et,El]
        return self
    def DutCalculation(self,sRaw):
        if self.numPorts==1:
            (Ed,Er,Es)=tuple(self.ET[0][0])
            gamma=sRaw[0][0]
            Gamma=(gamma-Ed)/((gamma-Ed)*Es+Er)
            return Gamma
        else:
            A=self._Zeros()
            B=self._Zeros()
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
