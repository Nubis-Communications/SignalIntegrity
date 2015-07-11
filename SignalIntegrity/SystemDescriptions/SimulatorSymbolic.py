from SystemSParametersSymbolic import SystemSParametersSymbolic
from Simulator import Simulator
from SignalIntegrity.Helpers import Matrix2LaTeX
from SignalIntegrity.Helpers import MatrixMultiply
from SignalIntegrity.Helpers import SubscriptedVector

class SimulatorSymbolic(SystemSParametersSymbolic, Simulator):
    def __init__(self,sd,**args):
        # self.Data=sd
        SystemSParametersSymbolic.__init__(self,sd,**args)
        Simulator.__init__(self, sd)
    def LaTeXTransferMatrix(self):
        self._LaTeXSi()
        veosi = MatrixMultiply(
            self.VoltageExtractionMatrix(self.pOutputList), self.SIPrime(True))
        veosi = Matrix2LaTeX(veosi, self._SmallMatrix())
#        sipr = Matrix2LaTeX(self.SIPrime(True), self._SmallMatrix())
#        veo = Matrix2LaTeX(
#            self.VoltageExtractionMatrix(self.pOutputList), self._SmallMatrix())
        on=Matrix2LaTeX(SubscriptedVector([D+str(P) for (D,P) in self.pOutputList]))
        sv=Matrix2LaTeX(SubscriptedVector(self.SourceVector()))
        sm=Matrix2LaTeX(self.SourceToStimsPrimeMatrix(True))
#        line = on+' = \\left[ '+veo+' \\cdot '+sipr+' \\right] \\cdot '+sm+'\\cdot '+sv
        line = on + '=' + veosi +'\\cdot '+sm+'\\cdot '+sv
        self._AddEq(line)
        return self
    def LaTeXEquations(self):
        self.LaTeXSystemEquation()
        self.LaTeXTransferMatrix2()
        return self