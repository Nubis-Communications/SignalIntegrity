"""Mutual inductance"""

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

# primary is ports 1 and 2, secondary is ports 3 and 4
# dot on ports 1 and 3
class Mutual(SParameters):
    """s-parameters of a mutual inductance"""
    def __init__(self,f,M,Z0=50.):
        """Constructor
        @param f list of frequencies.
        @param M float mutual inductance.
        @param Z0 (optional) float or complex reference impdedance (defaults to 50 Ohms).
        @remark
        This is a four-port device with no self inductance.\n
        The left leg is from port 1 to 2.\n
        The right leg is from port 3 to 4.\n
        The arrow for the mutual points to ports 1 and 3.\n
        The s-parameters are evaluated using the single-frequency device
        SignalIntegrity.Lib.Devices.Mutual
        """
        self.m_M=M
        SParameters.__init__(self,f,None,Z0)
    def __getitem__(self,n):
        """overloads [n]
        @return list of list s-parameter matrix for the nth frequency element
        """
        # pragma: silent exclude
        import SignalIntegrity.Lib.Devices as dev
        # pragma: include
        return dev.Mutual(0.,0.,self.m_M,self.m_f[n],self.m_Z0)
