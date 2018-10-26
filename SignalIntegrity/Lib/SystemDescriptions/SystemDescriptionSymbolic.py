"""
 Symbolic Solutions with System Descriptions
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

from SignalIntegrity.Lib.SystemDescriptions.SystemSParameters import SystemSParameters
from SignalIntegrity.Lib.SystemDescriptions.Symbolic import Symbolic
from SignalIntegrity.Lib.Helpers import SubscriptedVector

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
