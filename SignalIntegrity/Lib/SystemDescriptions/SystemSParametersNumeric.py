"""
 Computes Systems of Interconnected s-parameter blocks numerically
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

from numpy import matrix
from numpy import identity
from numpy import linalg

from SignalIntegrity.Lib.Helpers.AllZeroMatrix import *
from SignalIntegrity.Lib.SystemDescriptions.SystemSParameters import SystemSParameters
from SignalIntegrity.Lib.SystemDescriptions.Numeric import Numeric
from SignalIntegrity.Lib.Exception import SignalIntegrityExceptionNumeric

class SystemSParametersNumeric(SystemSParameters,Numeric):
    """Class for computing s-parameters of interconnected systems"""
    def __init__(self,sd=None):
        """ Constructor
        @param sd (optional) instance of class SystemDescription
        """
        SystemSParameters.__init__(self,sd)
    def SParameters(self,**args):
        """Calculates and returns the s-parameters.
        @param args named arguments (name=value).
        @return list of list s-parameter matrix containing the matrix for this frequency.
        the named arguments possible are:
        - 'solvetype' - either 'block' for the block solution or 'direct' for
        the direct solution.
        @todo document this better
        """
        from numpy.linalg.linalg import LinAlgError
        solvetype = args['solvetype'] if 'solvetype' in args else 'block'
        AN=self.PortBNames()
        BN=self.PortANames()
        if solvetype == 'direct':
            n=self.NodeVector()
            # pragma: silent exclude
            try:
            # pragma: include outdent
                PL=self.PermutationMatrix([n.index(BN[r])
                    for r in range(len(BN))], len(n))
                PR=matrix(self.PermutationMatrix([n.index(AN[r])
                    for r in range(len(AN))], len(n))).transpose()
                SCI=self.Dagger(matrix(identity(len(n)))-matrix(self.WeightsMatrix()),
                    Left=PL,Right=PR).tolist()
            # pragma: silent exclude indent
            except LinAlgError:
                raise SignalIntegrityExceptionNumeric('cannot invert I-W')
            # pragma: include
            B=[[0]*len(BN) for p in range(len(BN))]
            for r in range(len(BN)):
                for c in range(len(BN)):
                    B[r][c]=SCI[n.index(BN[r])][n.index(AN[c])]
            return B
        # else solvetype assumed to be 'block'
        XN=self.OtherNames(AN+BN)
        Wba=self.WeightsMatrix(BN,AN)
        Wxx=self.WeightsMatrix(XN,XN)
        if len(Wxx)==0:
            return matrix(Wba).tolist()
        Wbx=self.WeightsMatrix(BN,XN)
        Wxa=self.WeightsMatrix(XN,AN)
        if AllZeroMatrix(Wbx) or AllZeroMatrix(Wxa):
            return matrix(Wba).tolist()
        I=matrix(identity(len(Wxx)))
        # pragma: silent exclude
        try:
        # pragma: include outdent
            # Wba+Wbx*[(I-Wxx)^-1]*Wxa
            result = matrix(Wba)+self.Dagger(I-matrix(Wxx),Left=Wbx,Right=Wxa,Mul=True)
        # pragma: silent exclude indent
        except LinAlgError:
            raise SignalIntegrityExceptionNumeric('cannot invert I-Wxx')
        # pragma: include
        return result.tolist()