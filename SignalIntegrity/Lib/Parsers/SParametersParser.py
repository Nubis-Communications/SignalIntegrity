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

class SParametersParser(SParameters):
    """parses a list of commands to process s-parameters"""
    def __init__(self,sp,lines):
        """
        constructor

        takes a set of s-parameters along with a list of command lines to process the s-parameters

        @param sp instance of SParameters to process
        @param lines list of lines with commands indicating the processing, in order
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
                    else:
                        raise IndexError
            except IndexError:
                raise SignalIntegrityExceptionPostProcessing('not understood: '+line)
                    