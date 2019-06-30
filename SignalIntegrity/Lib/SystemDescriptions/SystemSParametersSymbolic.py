"""
SystemSParameters.py
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

from SignalIntegrity.Lib.Helpers.AllZeroMatrix import AllZeroMatrix
from SignalIntegrity.Lib.SystemDescriptions.SystemDescriptionSymbolic import SystemDescriptionSymbolic
from SignalIntegrity.Lib.SystemDescriptions.Device import Device
from SignalIntegrity.Lib.Helpers.AllZeroMatrix import *

class SystemSParametersSymbolic(SystemDescriptionSymbolic):
    """Class for solving symbolically the s-parameters of interconnected systems."""
    def __init__(self,sd=None,**args):
        """Constructor
        @param sd (optional) instance of class SystemDescription
        @param args (optional) named arguments (name = value)
        Named arguments passed to the Symbolic class
        @see Symbolic
        """
        SystemDescriptionSymbolic.__init__(self,sd,**args)
    def _LaTeXSi(self):
        sW=self._LaTeXMatrix(self.WeightsMatrix())
        self._AddEq('\mathbf{Si} = \\left[ '+self._Identity()+\
            ' - '+sW+' \\right]^{-1}')
        return self
    def LaTeXSolution(self,**args):
        """Calculates and stores internally a symbolic representation
        of the LaTeX s-parameter solution for the network.
        @param args named arguments (name=value).
        @return self
        the named arguments possible are:
        - 'solvetype' - (optional) either 'block' for the block solution or 'direct' for
        the direct solution (defaults to 'block').
        - 'size' - either 'normal', 'big', or 'biggest' (defaults to 'normal').
        @see Symbolic
        Here, 'size' is used depending on the size of the solution.
        If the size is normal, then the block solution is output in matrix form
        on one line.  If the size is big, the inverse of (I-Wxx) is shown on one line
        and Wxx is used on the next single line solution, as this tends to become
        large sometimes.  The biggest size is used when the solution is really large
        and it basically defines each matrix in the block solution on its own line
        and then writes the final result using the names of the matrices."""
        # pragma: silent exclude
        self.CheckConnections()
        # pragma: include
        solvetype = args['solvetype'] if 'solvetype' in args else 'block'
        size = args['size'] if 'size' in args else 'normal'
        AN=self.PortBNames(); BN=self.PortANames()
        if solvetype=='direct':
            self._LaTeXSi()
            BN=self.PortANames(); AN=self.PortBNames()
            n=self.NodeVector()
            SCI=Device.SymbolicMatrix('Si',len(n))
            B=[[0]*len(BN) for p in range(len(BN))]
            for r in range(len(BN)):
                for c in range(len(BN)):
                    B[r][c]=SCI[n.index(BN[r])][n.index(AN[c])]
            self._AddEq('\\mathbf{S} = '+self._LaTeXMatrix(B))
            return self
        XN=self.OtherNames(AN+BN)
        Wba=self.WeightsMatrix(BN,AN)
        sWba=self._LaTeXMatrix(Wba)
        Wxx=self.WeightsMatrix(XN,XN)
        if len(Wxx)==0:
            self._AddEq('\\mathbf{S} = '+sWba)
            return self
        Wbx=self.WeightsMatrix(BN,XN)
        Wxa=self.WeightsMatrix(XN,AN)
        if AllZeroMatrix(Wbx) or AllZeroMatrix(Wxa):
            self._AddEq('\\mathbf{S} = '+sWba)
            return self
        I=self._Identity()
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
            if AllZeroMatrix(I12) and AllZeroMatrix(Wxx12):
                Wbx=Wbx1
                Wxa=Wxa1
                I=self._LaTeXMatrix(I11)
                Wxx=Wxx11
        if XNzrWxa != []:
            if AllZeroMatrix(I21) and AllZeroMatrix(Wxx21):
                Wbx=Wbx1
                Wxa=Wxa1
                I=self._LaTeXMatrix(I11)
                Wxx=Wxx11
        # pragma: include
        sWbx=self._LaTeXMatrix(Wbx)
        sWxa=self._LaTeXMatrix(Wxa)
        sWxx=self._LaTeXMatrix(Wxx)
        if size=='biggest':
            if len(Wba) != 0: self._AddEq('\\mathbf{W_{ba}} = '+sWba)
            if len(Wbx) != 0: self._AddEq('\\mathbf{W_{bx}} = '+sWbx)
            if len(Wxa) != 0: self._AddEq('\\mathbf{W_{xa}} = '+sWxa)
            if len(Wxx) != 0: self._AddEq('\\mathbf{W_{xx}} = '+sWxx)
            self._AddEq('\\mathbf{S}=\\mathbf{W_{ba}}+\\mathbf{W_{bx}}\\cdot'+\
                '\\left[ '+I+\
                ' -\\mathbf{W_{xx}}\\right]^{-1}\\cdot\\mathbf{W_{xa}}')
        elif size=='big':
            self._AddEq('\\mathbf{Wi} = '+' \\left[ '+I+' - '+sWxx+' \\right]^{-1} ')
            # pragma: silent exclude
            if AllZeroMatrix(Wba):
                self._AddEq('\\mathbf{S} = '+sWbx+\
                    ' \\cdot \\mathbf{Wi} \\cdot' +sWxa)
            else:
                # pragma: include outdent
                self._AddEq('\\mathbf{S} = '+sWba+' + '+sWbx+\
                    ' \\cdot \\mathbf{Wi} \\cdot' +sWxa)
                # pragma: indent
        else:
            # pragma: silent exclude
            if AllZeroMatrix(Wba):
                self._AddEq('\\mathbf{S} = '+sWbx+' \\cdot \\left[ '+\
                I+' - '+sWxx+' \\right]^{-1} \\cdot'+sWxa)
            else:
                # pragma: include outdent
                self._AddEq('\\mathbf{S} = '+sWba+' + '+sWbx+' \\cdot \\left[ '+\
                I+' - '+sWxx+' \\right]^{-1} \\cdot'+sWxa)
                # pragma: indent
        return self
