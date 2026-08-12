"""MCB transmission-line device"""

# Copyright (c) 2021 Nubis Communications, Inc.
# Copyright (c) 2018-2020 Teledyne LeCroy, Inc.
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


class MCB(SParameters):
    """s-parameters of four-port MCB transmission line"""
    def __init__(self,f,Td=200e-12,lp=[1,2],rp=[3,4],Z0=50.):
        """Constructor
        @param f list of float frequencies
        @param Td float electrical length (propagation time)
        @param lp list of ints left ports in order (top to bottom)
        @param rp list of ints right ports in order (top to bottom)
        @param Z0 (optional) float or complex reference impedance (defaults to 50 ohms)
        """
        self.m_Td=Td
        self.m_lp=lp
        self.m_rp=rp
        SParameters.__init__(self,f,None,Z0)

    def __getitem__(self,n):
        """overloads [n]
        @return list of list s-parameter matrix for the nth frequency element
        """
        # pragma: silent exclude
        import SignalIntegrity.Lib.Devices as dev
        # pragma: include
        return dev.MCBFourPort(self.m_f[n],self.m_Td,self.m_lp,self.m_rp,self.m_Z0)
