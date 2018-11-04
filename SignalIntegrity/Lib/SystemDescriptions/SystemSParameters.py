"""
 System s-parameters base class
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

from SignalIntegrity.Lib.SystemDescriptions.SystemDescription import SystemDescription

class SystemSParameters(SystemDescription):
    """base class for housekeeping involving system s-parameters calculations"""
    def __init__(self,sd=None):
        SystemDescription.__init__(self,sd)
    def PortANames(self):
        return [x[1] for x in sorted
                ([(int(self[d].Name.strip('P')),self[d][0].A)
                  for d in range(len(self)) if self[d].Name[0]=='P'])]
    def PortBNames(self):
        return [x[1] for x in sorted
                ([(int(self[d].Name.strip('P')),self[d][0].B)
                  for d in range(len(self)) if self[d].Name[0]=='P'])]
    def OtherNames(self,K):
        other=[]
        for item in self.NodeVector():
            if not item in K: other.append(item)
        return other
    def NodeVector(self):
        return [self[d][p].B for d in range(len(self)) for p in range(len(self[d]))]
    def StimulusVector(self):
        return [self[d][p].M for d in range(len(self)) for p in range(len(self[d]))]
    def WeightsMatrix(self,ToN=None,FromN=None):
        """returns a weights matrix
        @protected
        @param ToN (optional) list of names of nodes To
        @param FromN (optional) list of name of node From
        @return a list of list matrix of weights such that if multiplied by the vector of nodes listed in FromN
        produces the nodes listed in ToN.
        """
        if not isinstance(ToN,list):
            nv = self.NodeVector()
            ToN = nv
        if not isinstance(FromN,list):
            FromN=ToN
        PWM = [[0]*len(FromN) for r in range(len(ToN))]
        for d in range(len(self)):
            for p in range(len(self[d])):
                if self[d][p].B in ToN:
                    r=ToN.index(self[d][p].B)
                    for c in range(len(self[d])):
                        if self[d][c].A in FromN:
                            ci=FromN.index(self[d][c].A)
                            PWM[r][ci]=self[d].SParameters[p][c]
        return PWM
