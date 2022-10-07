"""Lossy single-ended transmission line"""

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

class TLineLossy(SParameters):
    """s-parameters of ideal lossy single-ended transmission line"""
    def __init__(self,f,Zc,Td,LdBperHzpers=0,LdBperrootHzpers=0,Z0=50.):
        """Constructor
        @param f list of float frequencies
        @param Zc float or complex characteristic impedance
        @param Td float electrical length (propagation time)
        @param LdBperHzpers float (optional, defaults to zero) loss in dB/Hz/s
        @param LdBperrootHzpers float (optional,defaults to zero) skin-effect loss in dB/sqrt(Hz)/s
        @param Z0 (optional) float or complex reference impedance (defaults to 50 ohms) 
        @note losses are positive numbers for actual loss -- negative numbers are gain.
        """
        self.m_Zc=Zc;   self.m_Td=Td;   self.m_LdBperHzpers=LdBperHzpers; self.m_LdBperrootHzpers=LdBperrootHzpers
        SParameters.__init__(self,f,None,Z0)
    def __getitem__(self,n):
        """overloads [n]
        @return list of list s-parameter matrix for the nth frequency element
        """
        # pragma: silent exclude
        import SignalIntegrity.Lib.Devices as dev
        # pragma: include
        return dev.TLineTwoPortLossy(
                self.m_Zc,self.m_Td,self.m_f[n],self.m_LdBperHzpers,self.m_LdBperrootHzpers,self.m_Z0)

