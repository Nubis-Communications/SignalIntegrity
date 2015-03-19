from SystemDescription import SystemDescription
from Symbolic import Symbolic
from Device import Device

class SystemDescriptionSymbolic(SystemDescription,Symbolic):
    def __init__(self,sd,equationEnvironment=False,small=False):
        self.Data=sd
        Symbolic.__init__(self,equationEnvironment,small)
    def LaTeXSystemEquation(self):
        sW=self._LaTeXMatrix(self.WeightsMatrix())
        sn=self._LaTeXMatrix(self.SubscriptedVector(self.NodeVector()))
        sm=self._LaTeXMatrix(self.SubscriptedVector(self.StimulusVector()))
        self._AddEq('\\left[ '+self.Identity()+' - '+sW+'\\right] \\cdot '+\
            sn+' = '+sm)
        return self



