"""
Numeric.py
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

from SignalIntegrity.Lib.Devices import TeeThreePortSafe

class Numeric(object):
    alwaysUseSVD=False
    trySVD=True
    singularValueLimit=1e-6
    conditionNumberLimit=1e-12
    def InstallSafeTees(self,Z=0.00001):
        for d in range(len(self)):
            if '#' in self[d].Name:
                self[d].AssignSParameters(TeeThreePortSafe(0.000000001))
    def Dagger(self,A,Left=None,Right=None,returnType='matrix'):
        """
        Special computation of A^\dagger where L*A^\dagger *R needs to be computed
        @param A list if list matrix A to be inverted
        @param Left optional list of list matrix that appears to the left of A^\dagger
        @param Right optional List of list matrix that appears to the right of A^\dagger
        @return A^\dagger
        @throw LinAlgError if matrix cannot be inverted
        """
        from numpy import linalg,matrix,identity
        from numpy.linalg.linalg import LinAlgError,svd
        if A is None:
            return None
        if isinstance(A,list):
            a=A
            A=matrix(a)
        elif isinstance(A,matrix):
            a=A.tolist()

        if not self.alwaysUseSVD:
            try:
                # without this check, there is a gray zone where the matrix is really uninvertible
                # yet, produces total garbage without raising the exception.
                Adagger=A.getI()
                if linalg.cond(Adagger,p=-2) < self.conditionNumberLimit:
                    raise LinAlgError

                if returnType=='list': Adagger=Adagger.tolist()
                return Adagger

            except LinAlgError:
                # the regular matrix inverse failed
                if not self.trySVD:
                    raise LinAlgError

        if self.trySVD:
            U,sigma,VH = svd(A)
            u=U.tolist()
            vh=VH.tolist()
            sigma=sigma.tolist()
            R=len(a)
            C=len(a[0])
            if Left is None:
                Left=identity(R)
            if isinstance(Left,matrix):
                left=Left.tolist()
            elif isinstance(Left,list):
                left=Left
                Left=matrix(left)
            if Right is None:
                Left=identity(C)
            if isinstance(Right,matrix):
                right=Right.tolist()
            elif isinstance(Right,list):
                right=Right
                Right=matrix(right)
            LeftTimesV=Left*VH.getH()
            lefttimesv=LeftTimesV.tolist()
            UTimesRight=U.getH()*Right
            utimesright=UTimesRight.tolist()
            singularValueUsed=[False]*len(sigma)
            for r in range(len(utimesright)):
                for c in range(len(utimesright[0])):
                    if abs(utimesright[r][c])>self.singularValueLimit:
                        singularValueUsed[c]=True
            for r in range(len(lefttimesv)):
                for c in range(len(lefttimesv[0])):
                    if abs(lefttimesv[r][c])<self.singularValueLimit:
                        singularValueUsed[r]=False
            for i in range(len(singularValueUsed)):
                if not singularValueUsed[i]:
                    sigma=1.0
            
