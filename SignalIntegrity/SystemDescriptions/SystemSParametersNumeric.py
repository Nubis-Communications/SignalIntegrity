"""
 Computes Systems of Interconnected s-parameter blocks numerically
"""

# Copyright (c) 2018 Teledyne LeCroy, all rights reserved worldwide.
#
# This file is part of PySI.
#
# PySI is free software: You can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation, either version
# 3 of the License, or any later version.
#
# This program is distrbuted in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <https://www.gnu.org/licenses/>

from numpy import matrix
from numpy import identity
from numpy import linalg

from SignalIntegrity.Helpers.AllZeroMatrix import *
from SignalIntegrity.SystemDescriptions.SystemSParameters import SystemSParameters
from SignalIntegrity.SystemDescriptions.Numeric import Numeric
from SignalIntegrity.PySIException import PySIExceptionNumeric

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
                # I really hate this
                # without this check, there is a gray zone where the matrix is really uninvertible
                # yet, produces total garbage without raising the exception.
                # TODO: have Kavi take a look at this.
                if linalg.cond((matrix(identity(len(n)))-\
                    matrix(self.WeightsMatrix())).getI(),p=-2) < 1e-12: raise LinAlgError
            # pragma: include outdent
                SCI=((matrix(identity(len(n)))-\
                    matrix(self.WeightsMatrix())).getI()).tolist()
            # pragma: silent exclude indent
            except LinAlgError:
                raise PySIExceptionNumeric('cannot invert I-W')
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
        # pragma: exclude
        XNnzcWbx=[XN[nzcWbx] for nzcWbx in NonZeroColumns(Wbx)]
        XNzcWbx=[XN[zcWbx] for zcWbx in ZeroColumns(Wbx)]
        XNnzrWxa=[XN[nzrWxa] for nzrWxa in NonZeroRows(Wxa)]
        XNzrWxa=[XN[zrWxa] for zrWxa in ZeroRows(Wxa)]
        Wxx11=self.WeightsMatrix(XNnzrWxa,XNnzcWbx)
        Wxx12=self.WeightsMatrix(XNnzrWxa,XNzcWbx)
        Wxx21=self.WeightsMatrix(XNzrWxa,XNnzcWbx)
        Wxx22=self.WeightsMatrix(XNzrWxa,XNzcWbx)
        Wbx1=self.WeightsMatrix(BN,XNnzcWbx)
        Wbx2=self.WeightsMatrix(BN,XNzcWbx)
        Wxa1=self.WeightsMatrix(XNnzrWxa,AN)
        Wxa2=self.WeightsMatrix(XNzrWxa,AN)
        I11=[[1 if roele == coele else 0 for coele in XNnzcWbx] for roele in XNnzrWxa]
        I12=[[1 if roele == coele else 0 for coele in XNzcWbx] for roele in XNnzrWxa]
        I21=[[1 if roele == coele else 0 for coele in XNnzcWbx] for roele in XNzrWxa]
        I22=[[1 if roele == coele else 0 for coele in XNzcWbx] for roele in XNzrWxa]
        if XNzcWbx != []:
            if AllZeroMatrix((matrix(I12)-matrix(Wxx12)).tolist()):
                result=matrix(Wba)+matrix(Wbx1)*(I11-matrix(Wxx11)).getI()*matrix(Wxa1)
                return result.tolist()
        if XNzrWxa != []:
            if AllZeroMatrix((matrix(I21)-matrix(Wxx21)).tolist()):
                I = matrix(identity(len(Wxx11)))
                result=matrix(Wba)+matrix(Wbx1)*(I11-matrix(Wxx11)).getI()*matrix(Wxa1)
                return result.tolist()
        # pragma: include
        I=matrix(identity(len(Wxx)))
        # pragma: silent exclude
        try:
            # I really hate this
            # without this check, there is a gray zone where the matrix is really uninvertible
            # yet, produces total garbage without raising the exception.
            # TODO: have Kavi take a look at this.
            if linalg.cond(I-matrix(Wxx),p=-2) < 1e-12: raise LinAlgError
        # pragma: include outdent
            result = matrix(Wba)+matrix(Wbx)*(I-matrix(Wxx)).getI()*matrix(Wxa)
        # pragma: silent exclude indent
        except LinAlgError:
            raise PySIExceptionNumeric('cannot invert I-Wxx')
        # pragma: include
        return result.tolist()