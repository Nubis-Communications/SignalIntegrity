"""
 s-parameters post-processing parser
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

from SignalIntegrity.Lib.SParameters import SParameters
from SignalIntegrity.Lib.Exception import SignalIntegrityExceptionPostProcessing

class SParametersParser(SParameters):
    """parses a list of commands to process s-parameters"""
    def __init__(self,sp,lines):
        """Constructor  
        Takes a set of s-parameters along with a list of command lines to process the s-parameters
        @param sp instance of SParameters to process
        @param lines list of lines with commands indicating the processing, in order
        @remark For causality checks, the threshold for causality is 10e-6 (-100 dB).  
        The maximum number of iterations is 30.  
        the Largest singular value is 1.  
        @see EnforceCausality
        @see EnforcePassivity
        @see EnforceReciprocity
        @see EnforceBothPassivityAndReciprocity
        @see EnforceAll
        @see LimitImpulseResponseLength
        @todo For some reason the documentation does not show this class deriving from SParameters and needs to be fixed
        """
        SParameters.__init__(self,sp.m_f,sp.m_d,sp.m_Z0)
        for line in lines:
            tokens=line.split()
            try:
                if tokens[0]!='post':
                    continue
            except:
                pass
            try:
                if tokens[1]=='enforce':
                    if tokens[2]=='causality':
                        self.EnforceCausality()
                    elif tokens[2]=='passivity':
                        self.EnforcePassivity()
                    elif tokens[2]=='reciprocity':
                        self.EnforceReciprocity()
                    elif tokens[2]=='both':
                        self.EnforceBothPassivityAndCausality(causalityThreshold=10e-6,maxIterations=30,maxSingularValue=1.)
                    elif tokens[2]=='all':
                        self.EnforceAll(causalityThreshold=10e-6,maxIterations=30,maxSingularValue=1.)
                    else:
                        raise IndexError
                elif tokens[1]=='limit':
                    self.LimitImpulseResponseLength((float(tokens[2]) if tokens[2]!='none' else -1e15,
                                                     float(tokens[3]) if tokens[3]!='none' else +1e15))
                else:
                    raise IndexError
            except:
                raise SignalIntegrityExceptionPostProcessing('not understood: '+line)