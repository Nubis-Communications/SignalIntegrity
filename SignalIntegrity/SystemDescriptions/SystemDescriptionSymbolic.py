from SystemDescription import SystemDescription
from Symbolic import Symbolic
from Device import Device
from SignalIntegrity.Helpers import Matrix2LaTeX

class SystemDescriptionSymbolic(SystemDescription,Symbolic):
    def __init__(self,sd,equationEnvironment=False,small=False):
        self.Data=sd
        Symbolic.__init__(self,equationEnvironment,small)
    def LaTeXSystemEquation(self):
        W=self.WeightsMatrix()
        n=self.SubscriptedVector(self.NodeVector())
        m=self.SubscriptedVector(self.StimulusVector())
        self.AddLine(self.BeginEq() + '\\left[ ' + self.Identity() + ' - ' +\
            Matrix2LaTeX(W,self.SmallMatrix()) + '\\right] \\cdot '+ Matrix2LaTeX(n,self.SmallMatrix()) +\
            ' = '+ Matrix2LaTeX(m,self.SmallMatrix()) + self.EndEq())
        return self



