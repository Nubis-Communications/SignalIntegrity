"""one-port inductance"""

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

from SignalIntegrity.Lib.SParameters.SParameters import SParameters

class TerminationL(SParameters):
    """s-parameters of a termination (one-port) inductance"""
    def __init__(self,f,L,Z0=50.):
        """Constructor
        @param f list of float frequencies
        @param L float inductance
        @param Z0 (optional) float of complex reference impedance (defaults to 50 Ohms)
        @return the list of list s-parameter matrix for a termination inductance
        """
        self.m_L=L
        SParameters.__init__(self,f,None,Z0)
    def __getitem__(self,n):
        """overloads [n]
        @return list of list s-parameter matrix for the nth frequency element
        """
        # pragma: silent exclude
        import SignalIntegrity.Lib.Devices as dev
        # pragma: include
        return dev.TerminationL(self.m_L,self.m_f[n],self.m_Z0)
