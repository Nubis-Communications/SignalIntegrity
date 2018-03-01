"""
 Symbolic Solutions with System Descriptions
"""
# Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
# Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
# All Rights Reserved.
# 
# Explicit license in accompanying README.txt file.  If you don't have that file
# or do not agree to the terms in that file, then you are not licensed to use
# this material whatsoever.

from SignalIntegrity.SystemDescriptions.SystemSParameters import SystemSParameters
from SignalIntegrity.SystemDescriptions.Symbolic import Symbolic
from SignalIntegrity.Helpers import SubscriptedVector

class SystemDescriptionSymbolic(SystemSParameters,Symbolic):
    """Solves system descriptions in the most basic manner common to
    all of the simulation, system s-parameters, deembedding and virtual
    probing applications."""
    def __init__(self,sd=None,**args):
        """Constructor
        @param sd (optional) instance of class SystemDescription
        @param args (optional) named arguments (name = value)
        Named arguments passed to the Symbolic class
        @see Symbolic
        """
        SystemSParameters.__init__(self,sd)
        Symbolic.__init__(self,**args)
    def LaTeXSystemEquation(self):
        """Calculates and stores internally a symbolic representation
        of the LaTeX system equations for the network.
        @return self
        @see Symbolic
        """
        sW=self._LaTeXMatrix(self.WeightsMatrix())
        sn=self._LaTeXMatrix(SubscriptedVector(self.NodeVector()))
        sm=self._LaTeXMatrix(SubscriptedVector(self.StimulusVector()))
        self._AddEq('\\left[ '+self._Identity()+' - '+sW+'\\right] \\cdot '+\
            sn+' = '+sm)
        return self
