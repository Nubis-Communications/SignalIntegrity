"""
 ErrorTerms
"""

# Copyright (c) 2018 Teledyne LeCroy, Inc.
# All rights reserved worldwide.
#
# This file is part of SignalIntegrity.
#
# SignalIntegrity is free software: You can redistribute it and/or modify it under the terms
# of the GNU General Public License as published by the Free Software Foundation, either
# version 3 of the License, or any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <https://www.gnu.org/licenses/>

from numpy import matrix,zeros,identity
from numpy.linalg import det
from numpy.linalg import norm
import cmath

class ErrorTerms(object):
    """Error terms for VNA and TDR based s-parameter calculations.

    Error terms are, for P ports, a P x P matrix of lists of three error terms.
    For the diagonal elements, the three error terms are ED, ER, and ES in that order
    for the off diagonal elements, the three error terms are EX, ET and EL in that order
    for r in 0...P-1, and c in 0...P-1,  ET[r][c] = [ED[r],ER[r],ES[r]], when r==c
    ET[r][c]=[EX[r][c],ET[r][c],EL[r][c]] when r !=c

    ET[r][c] refers to the error terms at port r when driven at port c
    in other words, if r==c, then:
    ET[r][r][0] = EDr
    ET[r][r][1] = ERr
    ET[r][r][2] = ESr
    and when r!=c, then:
    ET[r][c][0]=EXrc
    ET[r][c][1]=ETrc
    ET[r][c][2]=ELrc
    """
    def __init__(self,ET=None):
        """Constructor
        @param ET (optional) instance of class ErrorTerms
        """
        self.ET=ET
        if not ET is None:
            self.numPorts=len(ET)
        else:
            self.numPorts=None
    def Initialize(self,numPorts):
        """Initialize

        Initializes the number of ports and all of the three error terms for
        each row and column of the error terms to zero.

        @param numPorts integer number of ports for the error terms
        @return self
        """
        self.numPorts=numPorts
        self.ET=[[[0.,0.,0.] for _ in range(self.numPorts)]
                 for _ in range(self.numPorts)]
        return self
    def InitializeFromFixtures(self,fixtureList):
        """Initialize from list of fixtures

        @param fixtureList list of list of list s-parameter fixture matrices
        @return self
        The number of matrices is the number of ports P and each matrix must be
        2P x 2P corresponding to the fixture format
        """
        self.Initialize(len(fixtureList))
        for r in range(len(fixtureList)):
            for c in range(len(fixtureList)):
                if r==c:
                    self.ET[r][r][0]=fixtureList[r][r][r]
                    self.ET[r][r][1]=fixtureList[r][r][r+self.numPorts]
                    self.ET[r][r][2]=fixtureList[r][r+self.numPorts][r+self.numPorts]
                else:
                    # Ex
                    self.ET[r][c][0]=fixtureList[c][r][c]
                    self.ET[r][c][1]=fixtureList[c][r][r+self.numPorts]
                    self.ET[r][c][2]=fixtureList[c][r+self.numPorts][r+self.numPorts]
        return self
    def __getitem__(self,item):
        """overloads [item]
        @param item integer row of the error term matrix to access
        @remark
        This is typically used to access an error term where self[o][d][i]
        would access the ith error term for port o with port d driven.
        """
        return self.ET[item]
    def ReflectCalibration(self,hatGamma,Gamma,m):
        """performs a reflect calibration

        Computes the directivity, reverse transmission, and source match terms
        for a given port and frequency from a list of measurements and actual standard
        values and updates itself.

        @param hatGamma list of complex measurements of reflect standards
        @param Gamma list of complex actual values of the reflect standards
        @param m integer index of port
        @return self
        """
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
        """performs a thru calibration

        Computes the forward transmission and load match terms
        for a given driven and undriven port and frequency from a list of measurements and actual
        standard values and updates itself.

        @param b1a1 list or single complex value for ratio of reflect to incident at driven port.
        @param b2a1 list or single complex value for ratio of reflect to incident at undriven port.
        @param S list or single list of list matrix representing s-parameters of thru standard
        @param n integer index of undriven port
        @param m integer index of driven port
        @return self
        """
        # pragma: silent exclude
        if not isinstance(b1a1,list):
            b1a1=[b1a1]
            b2a1=[b2a1]
            S=[S]
        # pragma: include
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
    def UnknownThruCalibration(self,Sm,Sest,firstPort,secondPort):
        """Computes the unknown thru

        for a given set of measurements of a thru and an estimate of the thru the actual value of the
        thru is calculated.

        @param Sm list of list raw sparameter measurement of the thru.
        @param Sest list of list estimate of the thru
        @param firstPort integer zero based port number of port 1 of thru standard
        @param secondPort integer zero based port number of port 2 of thru standard
        @return list of list sparameter value of the thru
        @remark normally this algorithm is used to compute the error terms directly (which are actually
        calculated here), but only the recovered thru value is returned.  This is so that an actual thru
        measurement can be created with this thru value.  If the thru measurement is provided with this
        calculated value of the thru, the error terms will be recalculated as calculated here, but returning
        the value of the thru allows the estimate to be checked for validity, and more importantly, allows
        for multiple thru measurements to be provided to allow for overconstrained, better calibrations.
        Additionally, the s-parameters of the entire thru measurement (not just at a single frequency) can be
        impulse response limited to provide an even more improved estimate of the thru.
        """
        # pragma: silent exclude
        # comment this in for debugging - it allows one to compare ET and EL calculated here with what it would
        # be with a known thru calibration
#         self.ThruCalibration(Sm[0][0], Sm[1][0],Sest,secondPort, firstPort)
#         self.ThruCalibration(Sm[1][1], Sm[0][1],[[Sest[1][1],Sest[1][0]],[Sest[0][1],Sest[0][0]]],firstPort,secondPort)
        # pragma: include
        [ED1,ER1,ES1]=self[firstPort][firstPort]
        [ED2,ER2,ES2]=self[secondPort][secondPort]
        [EX12,ET12,EL12]=self[firstPort][secondPort]
        [EX21,ET21,EL21]=self[secondPort][firstPort]
        p=cmath.sqrt((Sm[0][1]-EX12)/(Sm[1][0]-EX21))
        [EX12,ET12,EL12]=[EX12,cmath.sqrt(ER1)*cmath.sqrt(ER2)*p,ES1]
        [EX21,ET21,EL21]=[EX21,cmath.sqrt(ER1)*cmath.sqrt(ER2)/p,ES2]
        DutCalc1=ErrorTerms([[[ED1,ER1,ES1],[EX12,ET12,EL12]],
                             [[EX21,ET21,EL21],[ED2,ER2,ES2]]]).DutCalculation(Sm)
        DutCalc2=ErrorTerms([[[ED1,ER1,ES1],[EX12,-ET12,EL12]],
                             [[EX21,-ET21,EL21],[ED2,ER2,ES2]]]).DutCalculation(Sm)
        if norm(matrix(DutCalc1)-matrix(Sest)) < norm(matrix(DutCalc2)-matrix(Sest)):
            return DutCalc1
        else:
            return DutCalc2
    def ExCalibration(self,b2a1,n,m):
        """Computes the crosstalk term

         For a given driven and undriven port and frequency from a list of measurements and actual
         standard values and updates itself.

         @param b2a1 single complex value for ratio of reflect to incident at undriven port.
         @param n integer index of undriven port
         @param m integer index of driven port
         @return self
         """
        [_,Et,El]=self[n][m]
        Ex=b2a1
        self[n][m]=[Ex,Et,El]
        return self
    def TransferThruCalibration(self):
        """Performs the transfer thru calibrations.

        After all of the thru calibration calculations have been performed, it looks to see if there
        are any port combinations where a thru was not connected and attempts to perform the 'transfer
        thru' calibration that uses other thru measurements to form the thru calibration for a given
        port combination."""
        didOne=True
        while didOne:
            didOne=False
            for otherPort in range(self.numPorts):
                for drivenPort in range(self.numPorts):
                    if (otherPort == drivenPort):
                        continue
                    if ((self[otherPort][drivenPort][1]==0) and
                        (self[otherPort][drivenPort][2]==0)):
                        for mid in range(self.numPorts):
                            if ((mid != otherPort) and
                                (mid != drivenPort) and
                                ((self[otherPort][mid][1]!=0) or
                                 (self[otherPort][mid][2]!=0)) and
                                ((self[mid][drivenPort][1]!=0) or
                                 (self[mid][drivenPort][2]!=0))):
                                (_,Etl,_)=self[otherPort][mid]
                                (_,Etr,_)=self[mid][drivenPort]
                                (_,Erm,_)=self[mid][mid]
                                (_,_,Eso)=self[otherPort][otherPort]
                                (Ex,Et,El)=self[otherPort][drivenPort]
                                Et=Etl*Etr/Erm
                                El=Eso
                                self[otherPort][drivenPort]=[Ex,Et,El]
                                didOne=True
                                continue
        return self
    def Fixture(self,m,pl=None):
        """Fixture

        For a P port measurement, the s-parameters are for a 2*P port
        fixture containing the error terms when port m driven going between
        the insrument ports and the DUT ports where
        the first P ports are the instrument port connections and the remaining
        ports connect to the DUT.

        @param m integer driven port
        @param pl (optional) list of zero based port numbers of the DUT
        @return a list of list s-parameter matrix
        @remark If the portList is None, then it assumed to be a list [0,1,2,P-1] where P is the
        number of ports in sRaw, otherwise ports can be specified where the DUT is connected.
        m is assumed to be in integer zero based index in the ports list pl
        """
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
    def DutCalculationAlternate(self,sRaw,pl=None,reciprocal=False):
        """Alternate Dut Calculation
        @deprecated This provides a DUT calculation according to the Wittwer method,
        but a better,simpler method has been found.
        @param sRaw list of list s-parameter matrix of raw measured DUT
        @param pl (optional) list of zero based port numbers of the DUT
        @param reciprocal (optional, defaults to False) whether to enforce reciprocity
        @return list of list s-parameter matrix of calibrated DUT measurement
        @remark if reciprocity is True, the reciprocity is enforced in the calculation
        @see _EnforceReciprocity
        @see DutCalculation
        """
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
        if not reciprocal: S=(matrix(B)*matrix(A).getI()).tolist()
        else: S=self._EnforceReciprocity(A,B)
        return S
    def DutCalculation(self,sRaw,pl=None,reciprocal=False):
        """Calculates a DUT
        @param sRaw list of list s-parameter matrix of raw measured DUT
        @param pl (optional) list of zero based port numbers of the DUT
        @param reciprocal (optional, defaults to False) whether to enforce reciprocity
        @return list of list s-parameter matrix of calibrated DUT measurement
        @remark This provides a newer, simpler DUT calculation
        @remark If the portList is None, then it assumed to be a list [0,1,2,P-1] where P is the
        number of ports in sRaw, otherwise ports can be specified where the DUT is connected.
        @remark if reciprocity is True, the reciprocity is enforced in the calculation
        @see _EnforceReciprocity
        @see DutCalculationAlternate
        """
        P=len(sRaw); Pr=range(P)
        if pl is None: pl = [p for p in Pr]
        B=[[(sRaw[r][c]-self[pl[r]][pl[c]][0])/self[pl[r]][pl[c]][1]
            for c in Pr] for r in  Pr]
        A=[[B[r][c]*self[pl[r]][pl[c]][2]+(1 if r==c else 0) for c in Pr] for r in Pr]
        if not reciprocal: S=(matrix(B)*matrix(A).getI()).tolist()
        else: S=self._EnforceReciprocity(A,B)
        return S
    def _EnforceReciprocity(self,A,B):
        """Given S*A=B, Calculates a DUT in S enforcing reciprocity
        @param A list of list matrix
        @param B list of list matrix
        @return list of list s-parameter matrix of calibrated DUT measurement with reciprocity enforced
        @see DutCalculation, DutCalculationAlternate
        """
        P=len(A); Pr=range(P)
        M=[[None for _ in Pr] for _ in Pr]
        for c in Pr:
            for r in Pr:
                M[r][c]=M[c][r] if r < c else r-c+(0 if c==0 else M[P-1][c-1]+1)
        L=[[0. for c in range(P*(P+1)//2)] for r in range(P*P)]
        b=[None for r in range(P*P)]
        for r in Pr:
            for c in Pr:
                b[r*P+c]=[B[r][c]]
                for p in Pr: L[p*P+r][M[p][c]]=A[c][r]
        sv=(matrix(L).getI()*matrix(b)).tolist()
        S=[[sv[M[r][c]][0] for c in Pr] for r in Pr]
        return S
    def DutUnCalculation(self,S,pl=None):
        """undoes the DUT calculation
        @param S list of list s-parameter matrix a DUT
        @param pl (optional) list of zero based port numbers of the DUT
        @return list of list s-parameter matrix of raw measured s-parameters
        @remark If the portList is None, then it assumed to be a list [0,1,2,P-1] where P is the
        number of ports in sRaw, otherwise ports can be specified where the DUT is connected.
        """
        if pl is None: pl = [p for p in range(len(S))]
        Sp=[[None for c in range(len(S))] for r in range(len(S))]
        Si=matrix(S).getI()
        for c in range(len(S)):
            E=self.Fixture(c,pl)
            Em=[[matrix(E[0][0]),matrix(E[0][1])],[matrix(E[1][0]),matrix(E[1][1])]]
            col=(Em[0][0]*Em[1][0]+Em[0][1]*(Si-Em[1][1]).getI()*Em[1][0]).tolist()
            for r in range(len(S)): Sp[r][c]=col[r][c]
        return Sp
