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

from numpy import array
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
                PR=array(self.PermutationMatrix([n.index(AN[r])
                    for r in range(len(AN))], len(n))).transpose()
                SCI=self.Dagger(identity(len(n))-array(self.WeightsMatrix()),
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
            return array(Wba).tolist()
        Wbx=self.WeightsMatrix(BN,XN)
        Wxa=self.WeightsMatrix(XN,AN)
        if AllZeroMatrix(Wbx) or AllZeroMatrix(Wxa):
            return array(Wba).tolist()
        I=identity(len(Wxx))
        # pragma: silent exclude
        XNnzcWbx=[XN[nzcWbx] for nzcWbx in NonZeroColumns(Wbx)]
        XNzcWbx=[XN[zcWbx] for zcWbx in ZeroColumns(Wbx)]
        XNnzrWxa=[XN[nzrWxa] for nzrWxa in NonZeroRows(Wxa)]
        XNzrWxa=[XN[zrWxa] for zrWxa in ZeroRows(Wxa)]
        Wxx11=self.WeightsMatrix(XNnzrWxa,XNnzcWbx)
        Wxx12=self.WeightsMatrix(XNnzrWxa,XNzcWbx)
        Wxx21=self.WeightsMatrix(XNzrWxa,XNnzcWbx)
#       Wxx22=self.WeightsMatrix(XNzrWxa,XNzcWbx)
        Wbx1=self.WeightsMatrix(BN,XNnzcWbx)
#       Wbx2=self.WeightsMatrix(BN,XNzcWbx)
        Wxa1=self.WeightsMatrix(XNnzrWxa,AN)
#       Wxa2=self.WeightsMatrix(XNzrWxa,AN)
        I11=[[1 if roele == coele else 0 for coele in XNnzcWbx] for roele in XNnzrWxa]
        I12=[[1 if roele == coele else 0 for coele in XNzcWbx] for roele in XNnzrWxa]
        I21=[[1 if roele == coele else 0 for coele in XNnzcWbx] for roele in XNzrWxa]
#       I22=[[1 if roele == coele else 0 for coele in XNzcWbx] for roele in XNzrWxa]
        if XNzcWbx != []:
            if AllZeroMatrix(I12) and AllZeroMatrix(Wxx12):
                Wbx=Wbx1
                Wxa=Wxa1
                I=I11
                Wxx=Wxx11
        if XNzrWxa != []:
            if AllZeroMatrix(I21) and AllZeroMatrix(Wxx21):
                Wbx=Wbx1
                Wxa=Wxa1
                I=I11
                Wxx=Wxx11
        # pragma: include
        # pragma: silent exclude
        try:
        # pragma: include outdent
            # Wba+Wbx*[(I-Wxx)^-1]*Wxa
            result = array(Wba)+self.Dagger(I-array(Wxx),Left=Wbx,Right=Wxa,Mul=True)
        # pragma: silent exclude indent
        except LinAlgError:
            raise SignalIntegrityExceptionNumeric('cannot invert I-Wxx')
        # pragma: include
        return result.tolist()