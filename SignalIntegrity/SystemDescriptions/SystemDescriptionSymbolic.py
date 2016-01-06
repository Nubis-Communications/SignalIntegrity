'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
from SignalIntegrity.SystemDescriptions.SystemSParameters import SystemSParameters
from Symbolic import Symbolic
from SignalIntegrity.Helpers import SubscriptedVector

class SystemDescriptionSymbolic(SystemSParameters,Symbolic):
    def __init__(self,sd=None,**args):
        SystemSParameters.__init__(self,sd)
        Symbolic.__init__(self,**args)
    def LaTeXSystemEquation(self):
        sW=self._LaTeXMatrix(self.WeightsMatrix())
        sn=self._LaTeXMatrix(SubscriptedVector(self.NodeVector()))
        sm=self._LaTeXMatrix(SubscriptedVector(self.StimulusVector()))
        self._AddEq('\\left[ '+self._Identity()+' - '+sW+'\\right] \\cdot '+\
            sn+' = '+sm)
        return self



