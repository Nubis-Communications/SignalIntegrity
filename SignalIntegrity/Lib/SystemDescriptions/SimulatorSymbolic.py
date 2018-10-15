"""
 Symbolic Simulator
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

from SignalIntegrity.Lib.SystemDescriptions.SystemSParametersSymbolic import SystemSParametersSymbolic
from SignalIntegrity.Lib.SystemDescriptions.Simulator import Simulator
from SignalIntegrity.Lib.Helpers import Matrix2LaTeX
from SignalIntegrity.Lib.Helpers import MatrixMultiply
from SignalIntegrity.Lib.Helpers import SubscriptedVector

class SimulatorSymbolic(SystemSParametersSymbolic, Simulator):
    """class for producing symbolic solutions to simulation problems."""
    def __init__(self,sd=None,**args):
        """Constructor
        @param sd (optional) instance of class SystemDescription
        @param args (optional) named arguments (name = value)
        Named arguments passed to the Symbolic class
        @see Symbolic
        """
        SystemSParametersSymbolic.__init__(self,sd,**args)
        Simulator.__init__(self, sd)
    def LaTeXTransferMatrix(self):
        """Calculates and stores internally a symbolic representation
        of the transfer matrix in LaTeX.
        @return self
        @see Symbolic
        """
        self.Check()
        self._LaTeXSi()
        veosi = MatrixMultiply(
            self.VoltageExtractionMatrix(self.pOutputList), self.SIPrime(True))
        veosil = Matrix2LaTeX(veosi, self._SmallMatrix())
        if len(veosi)==1:
            if len(veosi[0])==1:
                veosil='\\left('+veosil+'\\right)'
        on=Matrix2LaTeX(SubscriptedVector([D+str(P) for (D,P) in self.pOutputList]))
        sv=Matrix2LaTeX(SubscriptedVector(self.SourceVector()))
        ssm=self.SourceToStimsPrimeMatrix(False)
        if len(ssm) == len(ssm[0]): # matrix is square
            isidentity=True
            for r in range(len(ssm)):
                for c in range(len(ssm[0])):
                    if r==c:
                        if ssm[r][c]!=1.:
                            isidentity=False
                            break
                    else:
                        if ssm[r][c]!=0.:
                            isidentity=False
                            break
        else: isidentity=False
        if isidentity:
            sm = ''
        else:
            sm=' \\cdot '+Matrix2LaTeX(self.SourceToStimsPrimeMatrix(True))
        line = on + '=' + veosil+sm+'\\cdot '+sv
        self._AddEq(line)
        return self
    def LaTeXEquations(self):
        """Calculates and stores internally a symbolic representation
        of the system equation and transfer matrix in LaTeX.
        @return self
        @see Symbolic for how to extract the stored result
        @see LaTeXTransferMatrix()
        @see LaTeXSystemEquation()
        """
        self.LaTeXSystemEquation()
        self.LaTeXTransferMatrix()
        return self