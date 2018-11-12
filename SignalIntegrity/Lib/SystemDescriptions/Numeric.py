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
    """handles numeric details of derived class solutions"""
    alwaysUseSVD=False
    trySVD=True
    singularValueLimit=1e-10
    conditionNumberLimit=1e-10
    #conditionNumberLimit=1e-6
    def InstallSafeTees(self,Z=0.00001):
        """obsolete
        @deprecated this function is no longer needed with the svd calculation.
        @see Dagger
        """
        for d in range(len(self)):
            if '#' in self[d].Name:
                self[d].AssignSParameters(TeeThreePortSafe(0.000000001))
    def Dagger(self,A,Left=None,Right=None,Mul=False):
        """
        Special computation of \f$\mathbf{A}^\dagger\f$ where
        \f$\mathbf{L}\cdot\mathbf{A}^\dagger\cdot\mathbf{R}\f$ needs to be computed\n
        @param A matrix \f$\mathbf{A}\f$ to be inverted
        @param Left optional matrix that appears to the left of \f$\mathbf{A}^\dagger\f$
        @param Right optional matrix that appears to the right of \f$\mathbf{A}^\dagger\f$
        @param Mul (optional) whether to provide the result \f$\mathbf{L}\cdot\mathbf{A}^\dagger\cdot\mathbf{R}\f$.
        Otherwise, by default, \$A^\dagger\f$ is returned.
        @return matrix \f$\mathbf{A}^\dagger\f$
        @throw LinAlgError if matrix cannot be inverted
        @remark All matrices supplied can be either list of list or numpy matrix, but
        the return type is always a numpy matrix
        @details if trySVD if False and alwaysUseSVD is False, then the Left and Right
        arguments are ignored and an attempt is made at calculating the Moore-Penrose
        pseudo-inverse of \f$\mathbf{A}\f$.  if the condition number of the resulting inverse is less
        than the conditionNumberLimit, then this method fails.\n
        If alwaysUseSVD is True or there is a failure and trySVD is True, then the svd
        is used.  The svd is not _better_ than the pseudo-inverse, per se, but it is able
        to make use of the left and right matrices.\n
        Many of the problems are of the form \f$\mathbf{L}\cdot\mathbf{A}^{-1}\cdot\mathbf{R}\f$.
        In many cases, the matrices \f$\mathbf{L}\f$
        and/or \f$\mathbf{R}\f$ are such that the all of the elements of the inverse of
        \f$\mathbf{A}\f$ are not used.
        Think of it as we only want to find certain elements of the inverse.  Situations like
        this arise, for example, when we have two wires in parallel connected to two circuit
        nodes.  We are not able to calculate the current through each of the wires, but we
        are able to calculate the current into and out of the parallel combination.  Another
        example is a circuit with no ground reference provided and we are calculating the
        differential voltage across an element in the circuit.  In cases like this, it is
        not possible to calculate the values of each circuit node, yet the answer exists and
        can be found.\n
        Using the svd, \f$\mathbf{A}\f$ is decomposed into \f$\mathbf{U}\cdot diag\left(\sigma\right)\cdot\mathbf{V}^H\f$
        where if \f$\mathbf{U}\f$ is \f$R\times C\f$, \f$diag\left(\sigma\right)\f$
        is \f$C\times C\f$ and \f$\mathbf{V}\f$ is \f$C\times C\f$.  The inverse of \f$\mathbf{A}\f$
        can be written as \f$\mathbf{V}\cdot diag\left(\sigma\right)^{-1}\cdot\mathbf{U}^H\f$.\n
        Here, we multiply the matrix \f$\mathbf{L}\cdot\mathbf{V}\f$ and the matrix \f$\mathbf{U}^H\cdot\mathbf{R}\f$.
        Then, if a column \f$rc\f$ of \f$\mathbf{L}\cdot\mathbf{V}\f$ is
        all zeros or a row \f$rc\f$ of \f$\mathbf{U}^H\cdot\mathbf{R}\f$ is zero,
        we know that the singular value \f$\sigma\left[rc\right]\f$ is
        not used and is irrelevant - we set it to one so that it can't harm us and return
        the inverse.
        @see trySVD
        @see alwaysUseSVD
        @see conditionNumberLimit
        @see singularValueLimit
        @throw LinAlgError if anything fails.
        """
        from numpy import linalg,matrix,diag
        from numpy.linalg.linalg import LinAlgError,svd
        if A is None: return None
        if isinstance(A,list): A=matrix(A)
        if not self.alwaysUseSVD:
            try:
                # without this check, there is a gray zone where the matrix is really uninvertible
                # yet, produces total garbage without raising the exception.
                if 1.0/linalg.cond(A) < self.conditionNumberLimit:
                    raise LinAlgError

                Adagger=A.getI()

                if Mul:
                    if Left is None: Left=1.
                    elif isinstance(Left,list):
                        Left=matrix(Left)
                        if Left.shape == (1,1):
                            Left=Left[0,0]
                    if Right is None: Right=1.
                    elif isinstance(Right,list):
                        Right=matrix(Right)
                        if Right.shape == (1,1):
                            Right=Right[0,0]
                    return Left*Adagger*Right
                else:
                    return Adagger
            except:
                # the regular matrix inverse failed
                pass # will get another try at it

        if self.trySVD:
            try:
                U,sigma,VH = svd(A,full_matrices=False)
                sigma=sigma.tolist()
                if Left is None: Left=1.
                elif isinstance(Left,list):
                    Left=matrix(Left)
                    if Left.shape == (1,1):
                        Left=Left[0,0]
                if Right is None: Right=1.
                elif isinstance(Right,list):
                    Right=matrix(Right)
                    if Right.shape == (1,1):
                        Right=Right[0,0]
                V=VH.getH()
                lv=(Left*V).tolist()
                UH=U.getH()
                uhr=(UH*Right).tolist()
                # assume that the singular value is unused according to left matrix
                sl=[False]*len(sigma)
                # if there is any element in column c that is nonzero
                # then the singular value is used
                for r in range(len(lv)):
                    for c in range(len(lv[0])):
                        if abs(lv[r][c])>self.singularValueLimit:
                            sl[c]=True
                # assume that the singular value is unused according to the right matrix
                sr=[False]*len(sigma)
                # if there is any element in column c that is nonzero
                # then the singular value is used
                for r in range(len(uhr)):
                    for c in range(len(uhr[0])):
                        if abs(uhr[r][c])>self.singularValueLimit:
                            sr[r]=True
                sUsed=[l and r for l,r in zip(sl,sr)]
                for u,s in zip(sUsed,sigma):
                    if u and (s<self.singularValueLimit):
                        raise LinAlgError
                sigmaInv=[1./self.singularValueLimit if (not sUsed[i] and s<self.singularValueLimit) else 1./sigma[i]
                        for i in range(len(sigma))]
                if Mul:
                    return matrix(lv)*matrix(diag(sigmaInv))*matrix(uhr)
                else:
                    return V*matrix(diag(sigmaInv))*UH
            except:
                raise LinAlgError
        else:
            raise LinAlgError
    def PermutationMatrix(self,rowList,Elements):
        """Row permutation matrix
        @param list of integer row elements to extract from matrix to right - in order
        @param Elements integer number of elements in matrix to right
        @return Row permutation matrix that if multiplied by matrix to the right, extracts
        the rows in rowList
        @note if the transpose of this matrix is post-multiplied by a matrix from the right,
        the columns in rowList would be exracted.
        """
        P=[[0 for _ in range(Elements)] for _ in range(len(rowList))]
        for r in range(len(rowList)): P[r][rowList[r]]=1
        return P
    ##
    # @var alwaysUseSVD
    # whether to always us the svd for matrix inverse computation.  The default is False
    # meaning that it first tries the numpy getI() for the moore-penrose pseudo-inverse.
    # If this fails or the condition number is poor, it will try again using svd if
    # trySVD is True.
    # @see trySVD
    # @var trySVD
    # whether to try the svd for matrix inverse computation.  The default is True.
    # If alwaysUseSVD is False,
    # then the first attempt is made without the svd.  If the first attempt fails, or
    # alwaysUseSVD is False, an attempt is made using the svd.
    # @see alwaysUseSVD
    # @var singularValueLimit
    # The limit on numbers that are multiplied by the inverse of the singular value before
    # they are considered zero.  Defaults to 1e-10.
    # @var conditionNumberLimit
    # The limit on the condition number of the inverse of the matrix before the matrix
    # inverse is considered suspect.  Defaults to 1e-1.

            
