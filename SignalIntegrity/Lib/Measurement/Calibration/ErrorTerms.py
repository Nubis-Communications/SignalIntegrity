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
        """
        self.numPorts=numPorts
        self.ET=[[[0.,0.,0.] for _ in range(self.numPorts)]
                 for _ in range(self.numPorts)]
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
    def Fixture(self,m):
        """Fixture

        For a P port measurement, the s-parameters are for a 2*P port
        fixture containing the error terms when port m driven going between
        the insrument ports and the DUT ports where
        the first P ports are the instrument port connections and the remaining
        ports connect to the DUT.

        @param m driven port
        @return a list of list s-parameter matrix
        """
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
        """Alternate Dut Calculation
        @deprecated This provides a DUT calculation according to the Wittwer method,
        but a better,simpler method has been found.
        @param sRaw list of list s-parameter matrix of raw measured DUT
        @return list of list s-parameter matrix of calibrated DUT measurement
        @see DutCalculation
        """
        if self.numPorts==1:
            (Ed,Er,Es)=self[0][0]
            gamma=sRaw[0][0]
            Gamma=(gamma-Ed)/((gamma-Ed)*Es+Er)
            return [[Gamma]]
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
        """Calculates a DUT
        @param sRaw list of list s-parameter matrix of raw measured DUT
        @return list of list s-parameter matrix of calibrated DUT measurement
        @remark This provides a newer, simpler DUT calculation
        @see DutCalculationAlternate
        """
        B=[[(sRaw[r][c]-self[r][c][0])/self[r][c][1] for c in range(len(sRaw))]
           for r in  range(len(sRaw))]
        A=[[B[r][c]*self[r][c][2]+(1 if r==c else 0) for c in range(len(sRaw))]
           for r in range(len(sRaw))]
        S=(matrix(B)*matrix(A).getI()).tolist()
        return S
