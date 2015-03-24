from SystemDescription import SystemDescription
from Symbolic import Symbolic
from Device import Device
from SignalIntegrity.Helpers import SubscriptedVector

class SystemDescriptionSymbolic(SystemDescription,Symbolic):
    def __init__(self,sd,**args):
        self.Data=sd
        Symbolic.__init__(self,**args)
    def LaTeXSystemEquation(self):
        sW=self._LaTeXMatrix(self.WeightsMatrix())
        sn=self._LaTeXMatrix(SubscriptedVector(self.NodeVector()))
        sm=self._LaTeXMatrix(SubscriptedVector(self.StimulusVector()))
        self._AddEq('\\left[ '+self._Identity()+' - '+sW+'\\right] \\cdot '+\
            sn+' = '+sm)
        return self



