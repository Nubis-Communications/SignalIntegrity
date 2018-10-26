"""Lossless single-ended transmission line"""

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

class TLineLossless(SParameters):
    """s-parameters of ideal lossless single-ended transmission line"""
    def __init__(self,f,P,Zc,Td,Z0=50.):
        """Constructor
        @param f list of float frequencies
        @param P integer number of ports (either 2 or 4)
        @param Zc float or complex characteristic impedance
        @param Td float electrical length (propagation time)
        @param Z0 (optional) float or complex reference impedance (defaults to 50 Ohms) 
        @note
        if two ports are specified, SignalIntegrity.Lib.Devices.TLineTwoPortLossless
        is used.\n
        Otherwise, if four ports are specified,
        SignalIntegrity.Lib.Devices.TLineFourPortLossless is used\n
        """
        self.m_Zc=Zc;   self.m_Td=Td;   self.m_P=P
        SParameters.__init__(self,f,None,Z0)
    def __getitem__(self,n):
        """overloads [n]
        @return list of list s-parameter matrix for the nth frequency element
        """
        # pragma: silent exclude
        import SignalIntegrity.Lib.Devices as dev
        # pragma: include
        if self.m_P==2: return dev.TLineTwoPortLossless(
                self.m_Zc,self.m_Td,self.m_f[n],self.m_Z0)
        elif self.m_P==4: return dev.TLineFourPortLossless(
                self.m_Zc,self.m_Td,self.m_f[n],self.m_Z0)
