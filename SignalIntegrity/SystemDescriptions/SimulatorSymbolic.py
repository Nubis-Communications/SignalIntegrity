"""
 Symbolic Simulator
"""
# Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
# Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
# All Rights Reserved.
# 
# Explicit license in accompanying README.txt file.  If you don't have that file
# or do not agree to the terms in that file, then you are not licensed to use
# this material whatsoever.

from SignalIntegrity.SystemDescriptions.SystemSParametersSymbolic import SystemSParametersSymbolic
from SignalIntegrity.SystemDescriptions.Simulator import Simulator
from SignalIntegrity.Helpers import Matrix2LaTeX
from SignalIntegrity.Helpers import MatrixMultiply
from SignalIntegrity.Helpers import SubscriptedVector

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
        veosi = Matrix2LaTeX(veosi, self._SmallMatrix())
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
        line = on + '=' + veosi+sm+'\\cdot '+sv
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