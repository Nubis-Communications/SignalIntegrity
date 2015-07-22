from SystemSParametersSymbolic import SystemSParametersSymbolic
from Simulator import Simulator
from SignalIntegrity.Helpers import Matrix2LaTeX
from SignalIntegrity.Helpers import MatrixMultiply
from SignalIntegrity.Helpers import SubscriptedVector

class SimulatorSymbolic(SystemSParametersSymbolic, Simulator):
    def __init__(self,sd=None,**args):
        SystemSParametersSymbolic.__init__(self,sd,**args)
        Simulator.__init__(self, sd)
    def LaTeXTransferMatrix(self):
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
        self.LaTeXSystemEquation()
        self.LaTeXTransferMatrix()
        return self